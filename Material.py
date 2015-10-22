import bpy

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
import bpy, os
from vb30.ui import classes
from vb30.lib import BlenderUtils, PathUtils


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
def Vray_tools_panel(self, context):
	
	layout = self.layout
	layout.operator("proxy.material_list")

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
		mat.vray.ntree.name = "Slot_" + str(i)
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
# Registration


 
if __name__ == "__main__":
	register()








	



