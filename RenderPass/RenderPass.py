import bpy  # , vb30
from vb30.plugins import PLUGINS_ID
from vb30.plugins.renderchannel import RenderChannelColor
from bpy.props import IntProperty, IntVectorProperty, StringProperty, BoolProperty, PointerProperty, BoolVectorProperty
from bpy.types import PropertyGroup


class RenderPassPanel(bpy.types.Panel):
	"""Creates a Panel in the Tools panel"""
	bl_label = "Vray Render Passes"
	bl_idname = "renderpass.panel"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "render_layer"

	def draw(self, context):
		scn = bpy.context.scene

		layout = self.layout

		obj = context.object
		sce = context.scene
		row = layout.row()
		row.operator('clear.passes')
		row.prop(scn, "RPassSwitch", text="On")
		row = layout.row()
		row = layout.row()

		# split = layout.split()
		col = layout.column_flow(columns=2, align=True)
		col.enabled = sce.RPassSwitch

		RenderPasses = RenderChannelColor.ColorChannelNamesMenu
		for i, passes in enumerate(RenderPasses):
			# col.enabled = scn.RPass[i]
			col.prop(scn, 'RPass', index=RPSettings.RPassCustom[i], text=RenderPasses[RPSettings.RPassCustom[i]][1], toggle=False)

		row = layout.row()
		col = layout.column_flow(columns=2, align=True)
		col.enabled = sce.RPassSwitch

		for i, passes in enumerate(RPSettings.RPassOther):
			col.prop(scn, 'RPassOther', index=i, text=passes[0], toggle=False)

class RPSettings():

	RPassCustom = [0,
	1, 21, 18,
	2, 15, 14,
	3, 17, 16,
	6, 4,
	7, 11, 23, 24,
	8, 10,
	9,
	5, 12, 22,
	20, 19, 25, 27, 29,
	28, 26, 13
	]

	RPassOther = [['Render ID', 'VRayNodeRenderChannelRenderID'],
				['Node ID',     'VRayNodeRenderChannelNodeID'],
				['MultiMatte',  'VRayNodeRenderChannelMultiMatte'],
				['Glossiness',  'VRayNodeRenderChannelGlossiness'],
				['ZDepth',      'VRayNodeRenderChannelZDepth'],
				]


class RenderPassGroup(bpy.types.PropertyGroup):
	juha = bpy.props.IntProperty()


def renderpass_onoff(self, context):
	scn = bpy.context.scene
	nodeout = scn.vray.ntree.nodes.get('Render Channles Container')
	RenderPasses = RenderChannelColor.ColorChannelNamesMenu

	for i, passes in enumerate(RenderPasses):
		if scn.RPassSwitch:
			nodeout.inputs[RPSettings.RPassCustom[i]].use = scn.RPass[RPSettings.RPassCustom[i]]
		else:
			nodeout.inputs[i].use = False


def renderpass_bool(self, context):
	scn = context.scene

	nodeout = scn.vray.ntree.nodes.get('Render Channles Container')
	RenderPasses = RenderChannelColor.ColorChannelNamesMenu

	for i, passes in enumerate(RenderPasses):
		nodeout.inputs[RPSettings.RPassCustom[i]].use = scn.RPass[RPSettings.RPassCustom[i]]
		print(i, ":", scn.RPass[RPSettings.RPassCustom[i]])

def renderpass_bool_other(self, context):
	scn = context.scene

	nodeout = scn.vray.ntree.nodes.get('Render Channles Container')
	startinput = len(RenderChannelColor.ColorChannelNamesMenu)

	for i, passes in enumerate(RPSettings.RPassOther):
		nodeout.inputs[startinput + i].use = scn.RPassOther[i]
		#print(i, ":", scn.RPass[RPSettings.RPassCustom[i]])

class ClearPasses(bpy.types.Operator):
	bl_idname = 'clear.passes'
	bl_label = "Clear passes"

	def node_create_color_channel(self, node_out, nodetree, RenderPasses):

		color_channel = []
		sizex = [140, 87]
		sizey = [176, 30]
		# create render pass nodes

		for i, passes in enumerate(RenderPasses):

			node = nodetree.nodes.new(type='VRayNodeRenderChannelColor')

			# render pass type
			node.RenderChannelColor.alias = RenderPasses[i][0]

			node.location.x = (i % 4) * sizex[1]
			node.location.y = 700 - (((i%4 * sizey[1])/2.5) + ((int(i/4) * sizey[1])*2))

			node.hide = True
			node.select = False
			# node name to RenderPasses names
			node.name = RenderPasses[i][1]

			# add input socket
			node_out.inputs.new(name='Channel', type='VRaySocketRenderChannel')
			# set renderpass off
			node_out.inputs[i].use = False
			# add socket name to RenderPasses names
			node_out.inputs[i].name = RenderPasses[i][1]

			# get linktree
			links = nodetree.links
			# link color nodes to Render channel node
			link = links.new(node.outputs[0], node_out.inputs[i])

			color_channel.append(node)

		return

	def node_create_renderid(self, node_out, nodetree, RenderPasses):

		sizex = [140, 87]
		sizey = [176, 30]

		for i, nlist in enumerate(RPSettings.RPassOther):

			nodetype = nlist[1]
			node = nodetree.nodes.new(type=nodetype)
			node.name = nlist[0]

			node.location.x = (i % 4) * sizex[1]
			node.location.y = 0 - (((i%4 * sizey[1])/2.5) + ((int(i/4) * sizey[1])*2))

			node.hide = True
			node.select = False

			# add input socket
			input = node_out.inputs.new(name='Channel', type='VRaySocketRenderChannel')
			# set renderpass off
			input.use = False
			# add socket name to RenderPasses names
			input.name = nlist[0]

			# get linktree
			links = nodetree.links
			# link color nodes to Render channel node
			link = links.new(node.outputs[0], input)

		return

	def execute(self, context):

		for area in bpy.context.screen.areas:
			if area.type == "NODE_EDITOR":
				override = {'screen': bpy.context.screen, 'area': area}

		scn = bpy.context.scene
		# clear render passes UI booleans
		RenderPasses = RenderChannelColor.ColorChannelNamesMenu
		scn.RPass = [False for x in range(len(RenderPasses))]
		scn.RPassOther = [False for x in range(len(RPSettings.RPassOther))]

		ng = bpy.data.node_groups
		LName = 'RenderPasses'
		RLayer = ng.new(LName, 'VRayNodeTreeScene') if LName not in ng else ng[LName]
		bpy.context.scene.vray.ntree = RLayer

		print("yes")

		# get nodetree
		nodetree = bpy.context.scene.vray.ntree
		nodes = nodetree.nodes
		nodes.clear()
		# create Render Channel node
		node_out = nodes.new('VRayNodeRenderChannels')
		# clear all input sockets
		node_out.inputs.clear()

		node_out.location.x = 600
		node_out.location.y = 800
		node_out.select = False

		self.node_create_color_channel(node_out, nodetree, RenderPasses)
		self.node_create_renderid(node_out, nodetree, RenderPasses)
		return {'FINISHED'}



#def register():





	#bpy.types.Scene.r = bpy.props.PointerProperty(type=RP.RenderPassGroup)
	#pass





#def unregister():



	# bpy.utils.unregister_class(RenderPassGroup)


	#pass
