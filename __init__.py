bl_info = {
	"name": "Vray Render Panel",
	"author": "JuhaW",
	"version": (0, 1, 0),
	"blender": (2, 76, 0),
	"location": "Tools",
	"description": "Quick Render Settings",
	"warning": "beta",
	"wiki_url": "",
	"category": "",
}

if "bpy" in locals():
	import imp
	if "Material" in locals():
		imp.reload(Material)

import sys
import bpy
from math import log
from bpy.props import *
import sys, os
import Vray_Render_Panel.Material



class HelloWorldPanel(bpy.types.Panel):
	"""Creates a Panel in the Tools panel"""
	bl_label = "Vray Render Settings"
	bl_idname = "OBJECT_PT_hello"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	# bl_context = "object"
	exposure = 0

	def draw(self, context):
		layout = self.layout

		obj = context.object
		sce = context.scene
		row = layout.row()


		#exposure()

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
			col.prop(sce.vray.SettingsGI, "secondary_engine", "Engine2")
			# Brute Force
			if sce.vray.SettingsGI.secondary_engine == '2':
				col.prop(sce.vray.SettingsDMCGI, "subdivs")
				col.prop(sce.vray.SettingsDMCGI, "depth")
			elif sce.vray.SettingsGI.secondary_engine == '3':
				# Light cache
				col.prop(sce.vray.SettingsLightCache, "mode", text="Mode")
				if sce.vray.SettingsLightCache.mode != '2':
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


		# --------------------------------------------------------------------
		# Camera, active
		cam = sce.camera.data.vray.CameraPhysical
		box = layout.box()
		row = box.row()

		row.prop(sce, "Camera", "", icon="TRIA_DOWN" if sce.Camera else "TRIA_RIGHT", icon_only=False, emboss=False)
		row.label("", icon="OUTLINER_OB_CAMERA" if cam.use else "CAMERA_DATA")
		row.prop(cam, "use", "Physical")
		row.label(context.scene.camera.name)


		if sce.Camera and cam.use:
			row = box.row()
			row.prop(sce,"Camera_Preserve_Exposure","Preserve Exposure")
			row.prop(sce, "f_number")
			#row.prop(sce,"f_number")
			row = box.row()
			row.prop(cam, "shutter_speed")

			if sce.Camera_Preserve_Exposure:
				row.enabled = False
			else:
				row.enabled = True

			row = box.row()


			#row = layout.row()
			#split = row.split()
			#col = split.column(align=True)
			#row.operator("exposure.get","Get F-number")
			#row.operator("exposure.set","Set Shutter")
			#row = box.row()
			row.prop(cam, "ISO")
			#
		# --------------------------------------------------------------------
		# Material
		box = layout.box()
		row = box.row()

		row.prop(sce, "Material", "", icon="TRIA_DOWN" if sce.Camera else "TRIA_RIGHT", icon_only=False, emboss=False)
		row.label("Viewport", icon="TEXTURE")

		if sce.Material:
			row = box.row()
			row.prop(sce,"Material_shadeless","Shadeless")
			row.operator("viewport.set")
#-------------------------------------------------------------------------------
class Viewport(bpy.types.Operator):
	bl_idname = "viewport.set"
	bl_label = "Show textures"

	def execute(self, context):

		sce = context.scene
		Material.create_textures(sce.Material_shadeless)
		return {'FINISHED'}
#-------------------------------------------------------------------------------
def exposure(self, context):

	scene = bpy.context.scene
	CameraPhysical= scene.camera.data.vray.CameraPhysical

	if scene.Camera_Preserve_Exposure:

		shutter = CameraPhysical.shutter_speed

		ape1 = round(log(round(pow(CameraPhysical.f_number, 2), 2), 2), 1)
		ape2 = round(log(round(pow(scene.f_number,2),2),2),1)
		#print ("ape1",ape1)
		#print ("ape2",ape2)
		CameraPhysical.shutter_speed = round(shutter * (pow(2,ape1 - ape2)))

	CameraPhysical.f_number = round(scene.f_number,2)
	#print ("self, context",self,context)
#-------------------------------------------------------------------------------

Engine1 = ["Irradiance", "", "Brute Force", "Light cache", "Spherical"]
Engine2 = ["None", "", "Brute Force", "Light cache"]
#bpy.context.scene.f_number = bpy.props.FloatProperty(update = shutter_update)

#-------------------------------------------------------------------------------


def register():
	bpy.utils.register_module(__name__)
	
	#bpy.utils.register_class(HelloWorldPanel)
	#bpy.utils.register_class(Viewport)
	bpy.types.Scene.GI = bpy.props.BoolProperty(default=True)
	bpy.types.Scene.Engines = bpy.props.BoolProperty(default=True)
	bpy.types.Scene.DMC = bpy.props.BoolProperty(default=True)
	bpy.types.Scene.Camera = bpy.props.BoolProperty(default=True)
	bpy.types.Scene.Camera_Preserve_Exposure = bpy.props.BoolProperty(default=True)

	bpy.types.Scene.shutter_speed = bpy.props.FloatProperty(name = "Shutter Speed", default=500.0, precision = 2,options={'HIDDEN'},subtype = 'NONE', unit = 'NONE')
	bpy.types.Scene.f_number = bpy.props.FloatProperty(name = "Aperture", default=8.0, precision = 2, update=exposure)

	bpy.types.Scene.Material = bpy.props.BoolProperty(default=True)
	bpy.types.Scene.Material_shadeless = bpy.props.BoolProperty(default=True)
	
	bpy.types.Scene.proxy_load_path = bpy.props.StringProperty \
      (
      name = "Root Path",
      default = "",
      description = "Proxy file path",
      subtype = 'FILE_PATH')
	  
	#bpy.utils.register_class(ProxyMaterialSave)
	#bpy.utils.register_class(ProxyMaterialLoad)
	
	bpy.types.VRAY_DP_tools.append(Material.Vray_tools_panel)
	
	  
	

def unregister():
	
	bpy.utils.unregister_module(__name__)
	
	#bpy.utils.unregister_class(HelloWorldPanel)
	#bpy.utils.unregister_class(Viewport)
	
	del bpy.types.Scene.GI
	del bpy.types.Scene.Engines
	del bpy.types.Scene.DMC
	del bpy.types.Scene.Camera
	del bpy.types.Scene.Camera_Preserve_Exposure
	#del bpy.types.Scene.Cam_exposure
	#del bpy.types.Scene.Cam_shutter_speed
	#del bpy.types.Scene.f_number
	del bpy.types.Scene.shutter_speed
	del bpy.types.Scene.Material
	del bpy.types.Scene.Material_shadeless
	del bpy.types.Scene.proxy_load_path
	bpy.types.VRAY_DP_tools.remove(Material.Vray_tools_panel)
	
	
if __name__ == "__main__":
	register()
