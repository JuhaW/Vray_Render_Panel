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
	print ("Material: ",mat)

	nodelist = []
	nodelist.append(nodeoutput)
	nodecounter = 0

	while nodecounter < len(nodelist):

		basenode = nodelist[nodecounter]

		if basenode.vray_plugin in ('TexBitmap','BitmapBuffer'):
			#print ("Mat:",mat.name, "has bitmap texture")
			try:
				image = bpy.data.node_groups[mat.name].nodes[basenode.name].texture.image
				return image
			except AttributeError:
				pass

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
	print ("##################################")

	for mat in bpy.data.materials:

		image = nodes_iterate(mat)

		mat.use_shadeless = shadeless
		mat.use_nodes = False
		
		#create image texture
		#print ("image:",image)
		if image:
			print ("image is not none")
			
			#create image texture if needed
			
			if mat.name in bpy.data.textures:
				tex = bpy.data.textures[mat.name]
			else:
				tex = bpy.data.textures.new(mat.name,'IMAGE')
			#mat.texture_slots.add()
			mat.texture_slots[0].texture  = tex
			mat.texture_slots[0].texture_coords = 'UV'
			mat.texture_slots[0].texture.image = image

###############################################################		
#nodes types with image
#bpy.data.materials[0].vray.ntree.nodes[3].vray_plugin,'TexBitmap','BitmapBuffer'

#output node
#bpy.data.materials[0].vray.ntree.nodes[1].bl_idname,'VRayNodeOutputMaterial'
