import bpy, os
from vb30.ui import classes
from vb30.lib import BlenderUtils, PathUtils
from vb30.nodes import importing as NodesImport
import re
import vb30
from bpy.props import *

global SLOT
SLOT = "_Slot_"

###############################################################

def outputnode_search(mat):
	#return node index
	
	for node in mat.vray.ntree.nodes:
		#print (i,node)
		if node.bl_idname == 'VRayNodeOutputMaterial' and node.inputs[0].is_linked:
			return node

	print ("No material output node found")
	return None
			
###############################################################
def nodes_iterate(mat):

	#return image/None

	nodeoutput = outputnode_search(mat)
	#print ("Material: ",mat)

	nodelist = []
	nodelist.append(nodeoutput)
	nodecounter = 0

	while nodecounter < len(nodelist):

		basenode = nodelist[nodecounter]

		if basenode.vray_plugin in ('TexBitmap','BitmapBuffer'):
			print ("Mat:",mat.name, "has bitmap texture")
			print ("basenode.name"	, basenode.name)

			if hasattr(basenode, 'texture'):
				if hasattr(basenode.texture, 'image'):
					image = basenode.texture.image
					print ("image=", image)
					return image

		inputlist = (i for i in basenode.inputs if i.is_linked)

		for input in inputlist:

			for nlinks in input.links:

				node = nlinks.from_node
				if node not in nodelist:
					nodelist.append(node)

		nodecounter +=1

	return None

###############################################################

def create_textures(shadeless):
	#print ("##################################")

	for mat in bpy.data.materials:

		image = nodes_iterate(mat)

		mat.use_shadeless = shadeless
		mat.use_nodes = False

		#create image texture
		#print ("image:",image)
		if image:
			#print ("image is not none")
			#print (mat.name)
			#create image texture if needed
			
			if mat.name in bpy.data.textures:
				tex = bpy.data.textures[mat.name]
			else:
				tex = bpy.data.textures.new(mat.name,'IMAGE')

			tex.image = image
			tex.type = 'IMAGE'
			#mat.texture_slots.add()
			#mat.texture_slots[0].texture  = tex
			#mat.texture_slots[0].texture.type	= 'IMAGE'
			#mat.texture_slots[0].texture_coords = 'UV'
			#mat.texture_slots[0].texture.image = image
			#mat.add_texture(texture = tex, texture_coordinates = 'UV')
			mat.texture_slots.clear(0)
			mat.texture_slots.add()
			mat.texture_slots[0].texture = tex
			mat.texture_slots[0].use_map_alpha = True

###############################################################		
#nodes types with image
#bpy.data.materials[0].vray.ntree.nodes[3].vray_plugin,'TexBitmap','BitmapBuffer'

#output node
#bpy.data.materials[0].vray.ntree.nodes[1].bl_idname,'VRayNodeOutputMaterial'
###############################################################		
#Proxy material save
###############################################################		



class ProxyMaterialList(bpy.types.Operator):
	bl_idname = "proxy.material_list"
	bl_label = "Save proxy materials"
	
	def execute(self, context):
		o = bpy.context.object
		GeomMeshFile = o.data.vray.GeomMeshFile

		# Create output path
		outputDirpath = BlenderUtils.GetFullFilepath(GeomMeshFile.dirpath)
		outputDirpath = PathUtils.CreateDirectory(outputDirpath)
		name = GeomMeshFile.filename

		outputfile = os.path.join(outputDirpath, name + '.txt')
		ret = '\n'
		blendpath = bpy.path.abspath(path= '//') + bpy.path.basename(bpy.context.blend_data.filepath)
		with open(outputfile, 'w') as w_file:
			  
			w_file.write(blendpath + ret + ret) 
			for mat in o.data.materials:
				w_file.write(mat.name + ret)

		print ("Vray Proxy materials saved:", outputfile)
		proxy_save_materials()
		
		return {'FINISHED'}
		
class ProxyMaterialLoad(bpy.types.Operator):
	bl_idname = "proxy.load_materials"
	bl_label = "Load proxy materials"
	
	filepath = StringProperty(name="File Path", description="Filepath for .vrscene", maxlen= 1024, default= "")
	files = CollectionProperty(
		name="File Path",
		type=bpy.types.OperatorFileListElement,
		)	 
		
	def execute(self, context):
	
		print (self.files[0].name)
		filepath =  self.properties.filepath
		
		#1
		matnames = store_materials()

		#2
		import_materials(filepath)

		#3
		matdifference = material_difference(matnames)

		#4
		materiallist = sort_materials(matdifference)

		#5	
		materials_add (materiallist)

		
		return {'FINISHED'}	
		
	def invoke(self, context, event):
		context.window_manager.fileselect_add(self)
		
		return {'RUNNING_MODAL'}
	
		
def Vray_tools_panel(self, context):
	
	layout = self.layout
	layout.operator("proxy.material_list")
	layout.operator("proxy.load_materials", icon = 'FILESEL')
	#layout.prop(context.scene, 'proxy_load_path')

	
def proxy_save_materials():
	
	#scene > node tools > path same than proxy export path
	GeomMeshFile = bpy.context.object.data.vray.GeomMeshFile
	outputDirpath = BlenderUtils.GetFullFilepath(GeomMeshFile.dirpath)
	bpy.context.scene.vray.Exporter.ntreeExportDirectory = PathUtils.CreateDirectory(outputDirpath)

	print ()
	print ("outputDirpath:",outputDirpath)
	print ()
	
	o = bpy.context.object
	
	filenames = []
	nodenames = []
	proxyname = o.data.vray.GeomMeshFile.filename
	
	#change node names
	for i, mat in enumerate(o.data.materials):

		nodename = mat.vray.ntree.name 
		nodenames.append(nodename)
		#print (i)
		#print (mat.name)
		#print ("nodename:", nodename)
		#mat.vray.ntree.name = proxyname + "_ProxyMat_" + mat.name + "_slot_" + str(i)
		mat.vray.ntree.name = proxyname + "_Slot_" + str(i)
		#print ("new nodename:",mat.vray.ntree.name)
		
		filenames.append(os.path.join(outputDirpath, mat.vray.ntree.name + '.vrscene'))
		
	#save nodes		   
	print ("Saving...")
	for mat in o.data.materials:
		
		nodename = mat.vray.ntree.name 
		print ("nodename:",nodename)
		i = bpy.data.node_groups.find(nodename)
		bpy.context.scene.vray.Exporter.ntreeListIndex = i
		bpy.ops.vray.export_nodetree()
		
	#change node names back to original
	for i, mat in enumerate(o.data.materials):
		mat.vray.ntree.name = nodenames[i]

	#print filenames
	
	for name in filenames:
		print ("Filename:", name)
	
	proxy_files_join(outputDirpath, filenames, proxyname)
	
def proxy_files_join(outputDirpath, filenames, proxyname):
		
	print()
	print ("proxy files join")
	print()
	print ("outputdirpath:", outputDirpath)
	print ("filenames:",filenames)
	
	filename = os.path.join(outputDirpath, proxyname + "_ProxyMaterials.vrscene")
	
	with open(filename, 'w') as outfile:
		for fname in filenames:
			with open(fname) as infile:
				for line in infile:
					outfile.write(line)

###############################################################		
#Proxy material load
###############################################################					
					
def import_materials(filepath):
	
	#filepath = "C:\Blender\Harjoituksia\Vray\proxy\Material_ProxyMaterials.vrscene"
	a = vb30.nodes.operators.import_file.ImportMaterials(bpy.context, filepath, 'STANDARD')

def print_materials():

	for mat in bpy.data.materials:
		print ("material:",mat.name)

def store_materials():
	matnames = []
	for mat in bpy.data.materials:
		matnames.append(mat.name)

	return matnames

def material_difference(matnames):
	matnames2 = []
	
	for mat in bpy.data.materials:
		matnames2.append(mat.name)
		
	matnames2 = set(matnames2)
	matnames3 = [x for x in matnames2 if x not in matnames]
	
	#print ("matnames:",matnames)
	#print ("matnames2:",matnames2)
	#print ("matnames3:", matnames3)
	
	return matnames3
	
def sort_materials(matnames):
	
	slotnumbers = []
	for mat in matnames:
		slotnumber = mat.split(SLOT)[1]
		slotnumber =  re.findall("\d+", slotnumber)[0]
		slotnumbers.append(int(slotnumber))
		#print ("Mat slotnumber : ", mat, slotnumber)
		
	materiallist = zip(slotnumbers,matnames)
	materiallist = list(materiallist)
	materiallist.sort()
	
	return materiallist

def materials_add(materialnames):	

	#clear object materials
	o = bpy.context.object
	omat = o.data.materials
	omat.clear()
	
	for i, mat in enumerate(materialnames):
		omat.append(bpy.data.materials[mat[1]])

					
					
# Registration

 
if __name__ == "__main__":
	register()








	



