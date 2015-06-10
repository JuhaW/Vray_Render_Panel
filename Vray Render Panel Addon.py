bl_info = {
	"name": "Vray Render Panel",
	"author": "JuhaW",
	"version": (0, 1, 0),
	"blender": (2, 74, 0),
	"location": "Tools",
	"description": "Quick Render Settings",
	"warning": "beta",
	"wiki_url": "",
	"category": "",
}

import bpy


Engine1 = ["Irradiance", "", "Brute Force", "Light cache", "Spherical"]
Engine2 = ["None", "", "Brute Force", "Light cache"]


class HelloWorldPanel(bpy.types.Panel):
	"""Creates a Panel in the Tools panel"""
	bl_label = "Vray Render Settings"
	bl_idname = "OBJECT_PT_hello"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	# bl_context = "object"

	def draw(self, context):
		layout = self.layout

		obj = context.object
		sce = context.scene
		row = layout.row()


		# row.label("",icon="VRAY_LOGO")
		row.prop(sce.vray.Exporter, "draft")
		row.prop(sce.vray.SettingsOptions, "light_doShadows")  # ,icon="INLINK")
		row = layout.row()
		row.prop(sce.vray.SettingsOptions, "mtl_glossy", "Glossy")
		row.prop(sce.vray.SettingsOptions, "mtl_reflectionRefraction", "Reflection")
		row.prop(sce.vray.SettingsOptions,"mtl_doMaps","Textures")
		row = layout.row()
		row.prop(sce.vray.SettingsOptions,"mtl_override_on","Material Override")
		if sce.vray.SettingsOptions.mtl_override_on:
			row.prop_search(sce.vray.SettingsOptions, 'mtl_override', bpy.data, 'materials', text="")

		# GI
		box = layout.box()
		row = box.row()
		row.prop(sce, "GI", icon="TRIA_DOWN" if sce.GI else "TRIA_RIGHT", icon_only=True, emboss=False)

		row.label("", icon="OUTLINER_OB_LAMP" if sce.vray.SettingsGI.on else "LAMP_DATA")
		row.prop(sce.vray.SettingsGI, "on", "GI")

		if sce.GI & sce.vray.SettingsGI.on:
			# box = layout.box()
			row = box.row()
			split = row.split()
			col = split.column(align=True)

			col.prop(sce.vray.SettingsOptions, "light_onlyGI", "GI only")
			col.prop(sce.vray.SettingsGI, "ao_on", "AO")
			col = split.column(align=True)
			col.prop(sce.vray.SettingsGI, "reflect_caustics")
			col.prop(sce.vray.SettingsGI, "refract_caustics")


		# Render Engines
		box = layout.box()
		row = box.row()

		row.prop(sce, "Engines", "", icon="TRIA_DOWN" if sce.Engines else "TRIA_RIGHT", icon_only=False, emboss=False)
		row.label("", icon="VRAY_LOGO_MONO")
		row.label("Engines")
		row.label(Engine1[int(sce.vray.SettingsGI.primary_engine)])
		row.label(Engine2[int(sce.vray.SettingsGI.secondary_engine)])

		if sce.Engines:

			# Create two columns, by using a split layout.
			# box = layout.box()
			row = box.row()
			split = row.split()

			# First column
			col = split.column(align=True)
			col.prop(sce.vray.SettingsGI, "primary_engine", "Engine1")

			# Irradiance map
			if sce.vray.SettingsGI.primary_engine == '0':

				col.prop(sce.vray.SettingsIrradianceMap, "mode", text="Mode")
				col.menu('VRayPresetMenuIM', text=bpy.types.VRayPresetMenuIM.bl_label)
				col.prop(sce.vray.SettingsIrradianceMap, "color_threshold")
				col.prop(sce.vray.SettingsIrradianceMap, "subdivs")
				col.prop(sce.vray.SettingsIrradianceMap, "interp_samples")
				col.prop(sce.vray.SettingsIrradianceMap, "auto_save")

			# Brute Force
			elif sce.vray.SettingsGI.primary_engine == '2':
				col.prop(sce.vray.SettingsDMCGI, "subdivs")
				col.prop(sce.vray.SettingsDMCGI, "depth")
			# Light Cache
			elif sce.vray.SettingsGI.primary_engine == '3':
				col.prop(sce.vray.SettingsLightCache, "mode", text="Mode")
				col.prop(sce.vray.SettingsLightCache, "subdivs")
				col.prop(sce.vray.SettingsLightCache, "sample_size")
				col.prop(sce.vray.SettingsLightCache, "depth")
				col.prop(sce.vray.SettingsLightCache, "adaptive_sampling")
				col.prop(sce.vray.SettingsLightCache, "auto_save")


			# Second column, aligned
			col = split.column(align=True)
			col.prop(sce.vray.SettingsGI, "secondary_engine", "Eengine2")
			# Brute Force
			if sce.vray.SettingsGI.secondary_engine == '2':
				col.prop(sce.vray.SettingsDMCGI, "subdivs")
				col.prop(sce.vray.SettingsDMCGI, "depth")
			elif sce.vray.SettingsGI.secondary_engine == '3':
				# Light cache
				col.prop(sce.vray.SettingsLightCache, "mode", text="Mode")
				col.prop(sce.vray.SettingsLightCache, "subdivs")
				col.prop(sce.vray.SettingsLightCache, "sample_size")
				col.prop(sce.vray.SettingsLightCache, "depth")
				col.prop(sce.vray.SettingsLightCache, "adaptive_sampling")
				col.prop(sce.vray.SettingsLightCache, "auto_save")

			row = box.row()
			row.prop(sce.vray.RTEngine, "enabled", "RT Engine")
			sub = row.split()
			sub.enabled = sce.vray.RTEngine.enabled
			sub.prop(sce.vray.RTEngine, "use_opencl")
		# --------------------------------------------------------------------
		# DMC

		box = layout.box()
		row = box.row()

		row.prop(sce, "DMC", "", icon="TRIA_DOWN" if sce.DMC else "TRIA_RIGHT", icon_only=False, emboss=False)
		row.label("", icon="VRAY_LOGO_MONO")
		row.label("DMC")

		if sce.DMC:
			row = box.row()
			split = row.split()

			# First column
			col = split.column(align=True)
			col.prop(sce.vray.SettingsImageSampler, "type")
			# bpy.context.scene.vray.SettingsImageSampler.type = '0'


def register():
	bpy.utils.register_class(HelloWorldPanel)
	bpy.types.Scene.GI = bpy.props.BoolProperty(default=True)
	bpy.types.Scene.Engines = bpy.props.BoolProperty(default=True)
	bpy.types.Scene.DMC = bpy.props.BoolProperty(default=True)


def unregister():
	bpy.utils.unregister_class(HelloWorldPanel)
	del bpy.types.Scene.GI
	del bpy.types.Scene.Engines
	del bpy.types.Scene.DMC


if __name__ == "__main__":
	register()
