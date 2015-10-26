import bpy, os
from vb30.ui import classes
from vb30.lib import BlenderUtils, PathUtils, LibUtils
from vb30.nodes import importing as NodesImport
import re
import vb30
from bpy.props import *
import bpy

from bpy.props import StringProperty, IntProperty


global SLOT
SLOT = "_ORIGINAL_"


###############################################################		
#Proxy material save
###############################################################		
class ProxyMaterialSave(bpy.types.Operator):
	'''Save all materials of selected object to .vrscene file'''
	bl_idname = "proxy.material_save"
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
		w_file.close()
		
		print ("Vray Proxy materials saved:", outputfile)
		proxy_save_materials()
		
		return {'FINISHED'}
###############################################################		
#Proxy material load
###############################################################					
class ProxyMaterialLoad(bpy.types.Operator):
	'''Load materials from .vrscene file and add them to the selected object'''
	bl_idname = "proxy.load_materials"
	bl_label = "Load proxy materials"
	
	filter_glob = StringProperty(default="*.vrscene", options={'HIDDEN'},)
	filepath = StringProperty(name="File Path", description="Filepath for .vrscene", maxlen= 1024, default= "")
	files = CollectionProperty(name="File Path", type=bpy.types.OperatorFileListElement,)	 
		
	def execute(self, context):
	
		print (self.files[0].name)
		filepath =	self.properties.filepath
		
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
	
###############################################################

def outputnode_search(mat): #return node/None
	
	for node in mat.vray.ntree.nodes:
		print (mat.name, node)
		if node.bl_idname == 'VRayNodeOutputMaterial' and node.inputs[0].is_linked:
			return node

	print ("No material output node found")
	return None
			
###############################################################
def nodes_iterate(mat, node_type_search = False): #return image/nodeindex/None
	#node_type_search = True when searching nodetype for proxy save

	nodeoutput = outputnode_search(mat)
	if nodeoutput is None:
		return None
	#print ("Material: ",mat)

	nodelist = []
	nodelist.append(nodeoutput)
	nodecounter = 0

	while nodecounter < len(nodelist):

		basenode = nodelist[nodecounter]
		
		#search nodetype
		if node_type_search:
			if node_type_check(basenode.vray_plugin):
				return mat.vray.ntree.nodes.find(basenode.name)
		#search image texture
		elif basenode.vray_plugin in ('TexBitmap','BitmapBuffer'):
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

	#filter out materials without nodetree
	materials = [m for m in bpy.data.materials if hasattr(m.vray.ntree, "name")]
	for mat in materials:

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


def Vray_tools_panel(self, context):
	
	layout = self.layout
	layout.operator("proxy.load_materials", icon = 'FILESEL')
	layout.operator("proxy.material_save")
	
		
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
		
		#get Material Output, check node type and change node name for later material slot order
		nodeindex = nodes_iterate(mat, True)
		mat.vray.ntree.nodes[nodeindex].name = SLOT + str(i)
		
		#print (i)
		#print (mat.name)
		#print ("nodename:", nodename)
		#mat.vray.ntree.name = proxyname + "_ProxyMat_" + mat.name + "_slot_" + str(i)
		
		#not sure about this
		#mat.vray.ntree.name = proxyname + SLOT + str(i)
		
		#print ("new nodename:",mat.vray.ntree.name)
		
		filenames.append(os.path.join(outputDirpath, LibUtils.CleanString(mat.vray.ntree.name) + '.vrscene'))
		
	#save nodes		   
	print ("Saving...")
	for mat in o.data.materials:
		
		nodename = mat.vray.ntree.name
		print ("Saving nodename:",nodename)
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

	print (len(o.data.materials), ": materials saved")  
	
def node_type_check(nodetype):
	
	MaterialTypeFilter = {
	'MtlSingleBRDF', 'MtlVRmat', 'MtlDoubleSided', 'MtlGLSL', 'MtlLayeredBRDF', 'MtlDiffuse',
	'MtlBump', 'Mtl2Sided', 'MtlMulti',
	'MtlWrapper',
	'MtlWrapperMaya', 'MayaMtlMatte', 'MtlMaterialID', 'MtlMayaRamp', 'MtlObjBBox',
	'MtlOverride', 'MtlRenderStats', 'MtlRoundEdges', 'MtlStreakFade'}
	
	return nodetype in MaterialTypeFilter
	
def proxy_files_join(outputDirpath, filenames, proxyname):
		
	
	print()
	print ("proxy files join")
	print()
	print ("outputdirpath:", outputDirpath)
	print ("filenames:",filenames)
	print ("proxyname:",proxyname)
	
	filename = os.path.join(outputDirpath, proxyname + "_ProxyMaterials.vrscene")
	print ("filename is:",filename)
	
	with open(filename, 'w+') as outfile:
		for fname in filenames:
			with open(fname) as infile:
				for line in infile:
					outfile.write(line)
	outfile.close()
					
def import_materials(filepath):
	
	#filepath = "C:\Blender\Harjoituksia\Vray\proxy\Material_ProxyMaterials.vrscene"
	a = vb30.nodes.operators.import_file.ImportMaterials(bpy.context, filepath, 'STANDARD')
	a = vb30.nodes.operators.import_file.ImportMaterials(bpy.context, filepath, 'MULTI')
	a = vb30.nodes.operators.import_file.ImportMaterials(bpy.context, filepath, 'WRAPPED')
	
def print_materials():

	for mat in bpy.data.materials:
		print ("material:",mat.name)

def store_materials():
	matnames = []
	for mat in bpy.data.materials:
		matnames.append(mat.name)

	return matnames

def material_difference(matnames):#return loaded material names
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
	print ("sorting materials")
	
	slotnumbers = []
	print ("matnames :", matnames)
	
	#material names which are not original materials
	matnot = [x for x in matnames if SLOT not in x or '@' in x]
	#delete material because its not original
	for matname in matnot:
		m = bpy.data.materials[matname]
		m.user_clear()
		bpy.data.materials.remove(m)

	#material names with original materials only
	matnames = [x for x in matnames if SLOT in x and '@' not in x]
	
	for mat in matnames:
		#node is named as "_original_" material
		slotnumber = mat.split(SLOT)[1]
		slotnumber =  re.findall("\d+", slotnumber)[0]
		slotnumbers.append(int(slotnumber))
		print ("Mat slotnumber : ", mat, slotnumber)

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


#get material output with input connection
#get next node which type is MaterialTypeFilter , MtlSingleBRDF etc.	
#change node filename to "ORIGINAL_" + material slot index
def run():
	o = bpy.context.object
	mat = o.active_material
	
		
	nodeindex = nodes_iterate(mat, True)
	mat.vray.ntree.nodes[nodeindex].name = "_ORIGINAL_"
	print ("nodetype found #", nodeindex, "type is:", bpy.data.node_groups[mat.name], mat.vray.ntree.nodes[nodeindex].vray_plugin)
	print()			

#run()
# Registration
