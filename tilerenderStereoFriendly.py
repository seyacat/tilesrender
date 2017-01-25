bl_info = {
    "name": "TileRender: Tile render frame by border",
    "author": "seyacat (Santiago Andrade)",
    "version": (1, 3),
    "blender": (2, 78, 0),
    "location": "View3D > Toolshelf > Edit Linked Library",
    "description": "Border based tile render",
    "warning": "",
    "wiki_url": "",
    "category": "Render",
    }

import bpy
import math
import numpy as np
import os
import re
import threading
from bpy.app.handlers import persistent
import subprocess
import time
  
        
class PanelTilerender(bpy.types.Panel):
    bl_label = "TileRender"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"

    @classmethod
    def poll(cls, context):
        return (True)
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        #icon = "OUTLINER_DATA_" + context.active_object.type
        layout.prop(scene.tilerender, "use_tilerender", text="Active Tilerender")
        layout.prop(scene.tilerender, "tilex", text="Tiles x")
        layout.prop(scene.tilerender, "tiley", text="Tiles y")
        layout.operator("render.tilerender_renderbackground", icon="NONE",text="Render")
        #layout.operator("render.tilerender_renderbackgroundimage", icon="NONE",text="Refresh Image")
        layout.operator("render.tilerender_showimage", icon="NONE",text="Refresh Image")
        #layout.prop(scene.tilerender, "log")
        
        col = layout.column()
        sub = col.row() # you may also use .column() here!
        #sub.enabled = False
        sub.prop(scene.tilerender, "timer", text="timer")
        sub.prop(scene.tilerender, "worker", text="WORKING")
        sub.prop(scene.tilerender, "render", text="RENDER")
        
        layout.operator("render.tilerender_removecache", icon="NONE",text="Remove Cache")
        
                       
class TilerenderProperties(bpy.types.PropertyGroup):
    use_tilerender = bpy.props.BoolProperty(
        name="Tilerender",
        description="Activa Tilerender",
        default=False)    
    timer = bpy.props.BoolProperty(
        name="Timer",
        description="Timer",
        default=False)
    worker = bpy.props.BoolProperty(
        name="Render Worker",
        description="Render Worker",
        default=False)
    render = bpy.props.BoolProperty(
        name="Image Render",
        description="Image Render",
        default=False)
    tilex = bpy.props.IntProperty(
        name="Tiles x",
        description="Tiles x",
        default=4)
    tiley = bpy.props.IntProperty(
        name="Tiles y",
        description="Tiles y",
        default=4)

class TilerenderRender(bpy.types.Operator):
    bl_idname = "render.tilerender_render"
    bl_label = "Render in tiles"

    def execute(self, context):
        n=bpy.context.scene.tilerender.tilex;
        m=bpy.context.scene.tilerender.tiley;
        blenderpath = bpy.app.binary_path.replace('\\','/')
        dirpath= bpy.path.abspath('//').replace('\\','/')
        filepath=bpy.data.filepath.replace('\\','/')
        filename=bpy.path.basename(filepath).replace('\\','/')
        pyfilename=filename+".py"  
        pyfullpath=os.path.join(dirpath,pyfilename).replace('\\','/')  
        #os.chdir(dirpath)  
        print("DIRPATH",dirpath);
        print("PYFILENAME",pyfilename);
        if filepath == "":
            return {'FINISHED'}
        pyfile="""PROCESSING""" 
        
        if not os.path.exists(pyfullpath):
            with open(pyfullpath, 'w') as out:
                out.write(pyfile) 
        
        #DEFINED SETTINGS
        #use_overwrite = bpy.context.scene.render.use_overwrite
        #use_placeholder = bpy.context.scene.render.use_placeholder
        use_border = bpy.context.scene.render.use_border
        #frame_start = bpy.context.scene.frame_start
        #frame_end = bpy.context.scene.frame_end
        
        frame = context.scene.frame_current
        fr = str(frame).zfill(4);
        ext=bpy.context.scene.render.file_extension
        bpy.context.scene.render.use_overwrite=False
        bpy.context.scene.render.use_placeholder=True
        bpy.context.scene.render.use_border=True
        bpy.context.scene.frame_start=frame
        bpy.context.scene.frame_end=frame
        
        if not os.path.exists(os.path.join(dirpath,'tilerender')):
            os.makedirs(os.path.join(dirpath,'tilerender'))         
        
        for i in range (0,n):
            for j in range(0,m):
                framepath= os.path.join(dirpath,'tilerender',filename+'_'+str(i)+"_"+str(j)+"_"+fr)
                bpy.context.scene.render.filepath=framepath         
                bpy.context.scene.render.border_min_x=(1.0/n)*i 
                bpy.context.scene.render.border_max_x=(1.0/n)*(i+1)
                bpy.context.scene.render.border_min_y=(1.0/m)*j
                bpy.context.scene.render.border_max_y=(1.0/m)*(j+1)
                if(bpy.context.scene.tilerender.worker):
                    if not os.path.exists(framepath+ext):
                        with open(framepath+ext, 'w') as out:
                            out.write("PLACEHOLDER")
                        bpy.ops.render.render(animation=False,write_still=True)
                    else:
                        pass
        
        
        
        #RESTORE SETTINGS
        #bpy.context.scene.render.use_overwrite = use_overwrite 
        #bpy.context.scene.render.use_placeholder = use_placeholder
        bpy.context.scene.render.use_border = use_border 
        #bpy.context.scene.frame_start = frame_start
        #bpy.context.scene.frame_end = frame_end
         
        #render 
        #os.chdir(dirpath)                                
                
        #Metodo1
        #cmd = '"%s" %s "%s" %s "%s"' % (blenderpath ,'-b', filepath, '-P' , pyfullpath)
        #print(cmd)
        #os.system(cmd) 
        
        #Metodo2
        #p=subprocess.Popen([blenderpath, '-b' ,filepath, '-P', pyfullpath ])
        #p.wait()
        if os.path.exists(pyfullpath):
            os.remove(pyfullpath);
        #bpy.ops.render.tilerender_renderbackgroundimage()
        return {'FINISHED'}

class TilerenderShowImage(bpy.types.Operator):
    bl_idname = "render.tilerender_showimage"
    bl_label = "Render Show Image"

    def execute(self, context):         
        bpy.context.scene.tilerender.render=True;
        dirpath= bpy.path.abspath('//') 
        filepath=bpy.data.filepath
        filename=bpy.path.basename(filepath) 
        frame = bpy.context.scene.frame_current
        fr = str(frame).zfill(4);
        img_name = 'tilerender_'+fr        
        if bpy.data.images.get(img_name) is not None :
            #bpy.data.images[img_name].name=img_name+"_old" 
            bpy.data.images[img_name].user_clear();
            bpy.data.images.remove( bpy.data.images[img_name] );

        #w = int(bpy.context.scene.render.resolution_x*bpy.context.scene.render.resolution_percentage/100)
        #h = int(bpy.context.scene.render.resolution_y*bpy.context.scene.render.resolution_percentage/100)
        #w = bpy.data.images[img_name].size[0]
        #h = bpy.data.images[img_name].size[1]
        #tilerender = bpy.ops.image.new(name=img_name,width=w,height=h,color=(0, 0, 0, 0))

        #tilerender =  bpy.data.images[img_name]
        #tilerender_pixels = np.array(tilerender.pixels[:])
        p = re.compile(filename+"_.*"+fr)
        
               
                 
        for imgname in os.listdir(os.path.join(dirpath,'tilerender')):                         
            fullPath = os.path.join( dirpath,'tilerender', imgname )                                
            if len(p.findall(fullPath)) > 0:                
                #bpy.ops.image.open( filepath = fullPath ) 
                img = bpy.data.images.load(fullPath)

                if bpy.data.images.get(img_name) is None :
                    w = img.size[0]
                    h = img.size[1]
                    tilerender = bpy.ops.image.new(name=img_name,width=w,height=h,color=(0, 0, 0, 0))
                    tilerender =  bpy.data.images[img_name]
                    tilerender_pixels = np.array(tilerender.pixels[:])
                    #p = re.compile(filename+"_.*"+fr)
            
                #img = bpy.data.images[bpy.path.basename(fullPath)]                              
                if img.size[0]==w and img.size[1]==h:
                    print(img)                      
                    tilerender_pixels = np.maximum( tilerender_pixels, np.array(img.pixels[:]) )
                    tilerender.pixels = tilerender_pixels.tolist()
                    screens = bpy.data.screens
                    for screen in screens:
                        for area in screen.areas:
                            if area.type == 'IMAGE_EDITOR' :                
                                    area.spaces.active.image = tilerender
                img.user_clear();
                bpy.data.images.remove( img );
            
            
        
        
        return {'FINISHED'}

    
   
class TilerenderRemoveCache(bpy.types.Operator):
    bl_idname = "render.tilerender_removecache"
    bl_label = "Delete Tiles"

    def execute(self, context): 
        dirpath= bpy.path.abspath('//')
        filepath=bpy.data.filepath
        filename=bpy.path.basename(filepath)
        pyfilename=filename+".py" 
        os.chdir(dirpath) 
        for imgname in os.listdir(os.path.join(dirpath,'tilerender')): 
            fullPath = os.path.join( dirpath,'tilerender', imgname )
            p = re.compile(filename+"_.*") 
            if len(p.findall(fullPath)) > 0:                
                os.remove(fullPath)
        return {'FINISHED'}
    
class TilerenderWorker(threading.Thread):
    def __init__(self):
        #self.values = values        
        threading.Thread.__init__(self)
    def run(self):
        if not bpy.context.scene.tilerender.worker:
            bpy.context.scene.tilerender.worker=True;
            bpy.ops.render.tilerender_render();
            bpy.context.scene.tilerender.worker=False;
 
class TilerenderRenderBackground(bpy.types.Operator):
    bl_idname = "render.tilerender_renderbackground"
    bl_label = "Render Background"

    def execute(self, context): 
        thread = TilerenderWorker()
        thread.start()
        return {'FINISHED'}
    
    
class TilerenderWorkerImage(threading.Thread):
    def __init__(self):
        #self.values = values        
        threading.Thread.__init__(self)
    def run(self):
        if not bpy.context.scene.tilerender.render:
            bpy.context.scene.tilerender.render=True;
            #bpy.ops.render.tilerender_showimage();
            bpy.context.scene.tilerender.render=False;
class TilerenderRenderBackgroundImage(bpy.types.Operator):
    bl_idname = "render.tilerender_renderbackgroundimage"
    bl_label = "Render Background Image"

    def execute(self, context): 
        thread = TilerenderWorkerImage()
        thread.start()
        return {'FINISHED'}

class TilerenderTimerOperator(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "render.tilerender_timer"
    bl_label = "Modal Timer Operator"
    _timer = None    
    def alerta(self,context):        
        dirpath= bpy.path.abspath('//')
        filepath=bpy.data.filepath
        filename=bpy.path.basename(filepath)
        pyfilename=filename+".py" 
        pyfullpath=os.path.join(dirpath,pyfilename) 
        #print(os.path.join(dirpath,pyfilename) ) 
        #os.chdir(dirpath) 
        if bpy.context.scene.tilerender.use_tilerender and os.path.exists(pyfullpath):
            bpy.ops.render.tilerender_renderbackground()
        
        if os.path.exists( os.path.join(dirpath,'tilerender') ):
            for imgname in os.listdir(os.path.join(dirpath,'tilerender')):
                #print ("last modified: %s" % os.path.getmtime(os.path.join( 'tilerender', imgname )) )
                #print ("created: %s" % os.path.getctime(os.path.join( 'tilerender', imgname )) )
                dtime = time.time() - os.path.getmtime( os.path.join( dirpath, 'tilerender' , imgname) )                 
                if(dtime < 5):
                    bpy.ops.render.tilerender_renderbackgroundimage()
        ##REPORTA ACTIVIDAD
        #thread = AlertWorker()
        #thread.start()
    def modal(self, context, event):
        if event.type == 'TIMER':
            self.alerta(context);
        return {'PASS_THROUGH'}
    def execute(self, context):
        wm = context.window_manager
        self._timer = wm.event_timer_add(5, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

@persistent
def onload(scene):    
    bpy.context.scene.tilerender.timer = False; 
    
@persistent
def onscene(scene):    
    #if bpy.context.scene.tilerender.use_tilerender and not bpy.context.scene.tilerender.timer:
    if not bpy.context.scene.tilerender.timer:
        bpy.context.scene.tilerender.timer = True; 
        bpy.ops.render.tilerender_timer();
                          
def register(): 
    #comment
    #for i in range( len( bpy.app.handlers.scene_update_post ) ):
    #    bpy.app.handlers.scene_update_post.pop()
    #for i in range( len( bpy.app.handlers.load_post ) ):
    #    bpy.app.handlers.load_post.pop()
    #end comment    
    bpy.utils.register_class(TilerenderRender)   
    bpy.utils.register_class(TilerenderShowImage)   
    bpy.utils.register_class(TilerenderRemoveCache) 
    bpy.utils.register_class(TilerenderProperties)
    bpy.utils.register_class(TilerenderRenderBackground)
    bpy.utils.register_class(TilerenderRenderBackgroundImage)
    bpy.types.Scene.tilerender = bpy.props.PointerProperty(type=TilerenderProperties)
    bpy.utils.register_class(PanelTilerender)
    bpy.utils.register_class(TilerenderTimerOperator)
    bpy.app.handlers.load_post.append( onload );
    bpy.app.handlers.scene_update_post.append( onscene );
    
def unregister():  
    bpy.utils.unregister_class(TilerenderRender) 
    bpy.utils.unregister_class(TilerenderShowImage)
    bpy.utils.unregister_class(TilerenderRemoveCache)    
    bpy.utils.unregister_class(TilerenderProperties)
    bpy.utils.unregister_class(TilerenderRenderBackground)
    bpy.utils.unregister_class(TilerenderRenderBackgroundImage)
    bpy.utils.unregister_class(PanelTilerender)
    del bpy.types.Scene.tilerender
    bpy.utils.unregister_class(TilerenderTimerOperator)
    bpy.app.handlers.load_post.remove( onload );
    bpy.app.handlers.scene_update_post.remove( onscene );
    
if __name__ == "__main__":
    register()