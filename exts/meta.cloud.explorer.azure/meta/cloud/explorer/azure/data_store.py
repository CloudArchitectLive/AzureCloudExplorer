
__all__ = ["Save_Config_Data", "Load_Config_Data"]

import carb
from .Singleton import Singleton
import omni.ui as ui
from .combo_box_model import ComboBoxModel
import pickle


@Singleton
class DataStore():
    def __init__(self):

        print("DataStore initialized")

        #Azure Resoruce Groups
        #NAME,SUBSCRIPTION,LOCATION
        self._groups = {}

        #All the reosurces
        #NAME,TYPE,RESOURCE GROUP,LOCATION,SUBSCRIPTION, LMCOST
        self._resources = {}        

        #aggregated data (counts)
        self._aad_count = {}
        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}
        self._type_count = {}
        self._tag_count = {}

        #aggregated data (costs)
        self._aad_cost = {}
        self._subscription_cost = {}
        self._location_cost = {}
        self._group_cost = {}
        self._type_cost = {}
        self._tag_cost = {}

        #mapped resources (indexes)
        #sample json format: (key(group), values[{}])
        #map_obj = {"name": resName, "type":typeName, "shape":shape, "location":loc, "subscription":sub, "group":grp, "cost":cost }
        self._map_aad = {}
        self._map_subscription = {}
        self._map_location = {}
        self._map_group = {}
        self._map_type = {}
        self._map_tag = {}

        #track where the data last came from (state)
        self._source_of_data = ""
        self._use_symmetric_planes = False
        self._use_packing_algo = True
        self._last_view_type = "ByGroup" # ByGroup, ByLocation, ByType, BySub, ByTag
        self._scale_model = 1.0

        #temporary arrays
        #Calc Plane sizes based on items in group
        self._lcl_sizes = [] #Plane  sizes determined by resource counts
        self._lcl_groups = [] #Group data for creating planes
        self._lcl_resources = [] #Resources to show on stage


        #Variables for files to import (UI settings)
        self._rg_csv_file_path = ""
        self._rg_csv_field_model = ui.SimpleStringModel()
        self._rs_csv_file_path = ""        
        self._rs_csv_field_model = ui.SimpleStringModel()
        self._bgl_file_path = ""        
        self._bgl_field_model = ui.SimpleStringModel()
        self._bgm_file_path = ""        
        self._bgm_field_model = ui.SimpleStringModel()
        self._bgh_file_path = ""        
        self._bgh_field_model = ui.SimpleStringModel()

        #azure connection info 
        self._azure_tenant_id = ""
        self._azure_tenant_id_model =ui.SimpleStringModel()
        self._azure_client_id = ""
        self._azure_client_id_model = ui.SimpleStringModel()
        self._azure_client_secret = ""
        self._azure_client_secret_model = ui.SimpleStringModel()
        self._azure_subscription_id = ""
        self._azure_subscription_id_model = ui.SimpleStringModel()

        #composition options (UI settings)
        self._symmetric_planes_model = ui.SimpleBoolModel(False)
        self._packing_algo_model = ui.SimpleBoolModel(True)
        self._primary_axis_model = ComboBoxModel("Z", "X", "Y") # track which Axis is up
        self._shape_up_axis_model = ComboBoxModel("Z", "X", "Y") # track which Axis is up for the shape placement
        self._composition_scale_model = ui.SimpleFloatModel()
        self._options_count_models = [ui.SimpleIntModel(), ui.SimpleIntModel(), ui.SimpleIntModel()]
        self._options_dist_models = [ui.SimpleFloatModel(), ui.SimpleFloatModel(), ui.SimpleFloatModel()]
        self._options_random_models = [ui.SimpleFloatModel(), ui.SimpleFloatModel(), ui.SimpleFloatModel()]

        self._composition_scale_model.as_float = 1.0
        self._options_count_models[0].as_int = 10
        self._options_count_models[1].as_int = 10
        self._options_count_models[2].as_int = 1
        self._options_dist_models[0].as_float = 250
        self._options_dist_models[1].as_float = 250
        self._options_dist_models[2].as_float = 250
        self._options_random_models[0].as_float = 1.0
        self._options_random_models[1].as_float = 1.0
        self._options_random_models[2].as_float = 1.0
        self.Load_Config_Data()


    def wipe_data(self):
        self._groups.clear()
        self._resources.clear()

        self._subscription_count = {}
        self._location_count = {}
        self._group_count = {}
        self._type_count = {}
        self._tag_count = {}

        self._subscription_cost = {}
        self._location_cost = {}
        self._group_cost = {}
        self._type_cost = {}
        self._tag_cost = {}
        
        self._map_aad = {}
        self._map_subscription = {}
        self._map_location = {}
        self._map_group = {}
        self._map_type = {}
        self._map_tag = {}

        self._lcl_sizes = [] 
        self._lcl_groups = [] 
        self._lcl_resources = [] 

        carb.log_info("Data Cleared.")


    def Save_Config_Data(self):
        settings = carb.settings.get_settings()
        if self._rg_csv_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/rg_csv_file_path", self._rg_csv_file_path)
        if self._rs_csv_file_path != "":            
            settings.set("/persistent/exts/meta.cloud.explorer.azure/rs_csv_file_path", self._rs_csv_file_path)
        if self._azure_tenant_id != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/azure_tenant_id", self._azure_tenant_id)
        if self._azure_client_id != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/azure_client_id", self._azure_client_id)
        if self._azure_subscription_id != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/azure_subscription_id", self._azure_subscription_id)
        if self._source_of_data != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/last_data_source", self._source_of_data)
        if self._bgl_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/bgl_file_path", self._bgl_file_path)
        if self._bgm_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/bgm_file_path", self._bgm_file_path)
        if self._bgh_file_path != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/bgh_file_path", self._bgh_file_path)
        if self._last_view_type != "":
            settings.set("/persistent/exts/meta.cloud.explorer.azure/last_view_type", self._last_view_type)
        if self._options_count_models[0].as_int >0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/x_group_count", self._options_count_models[0].as_int)
        if self._options_count_models[1].as_int >0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/y_group_count", self._options_count_models[1].as_int)
        if self._options_count_models[2].as_int >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/z_group_count", self._options_count_models[2].as_int)            
        if self._options_dist_models[0].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/x_dist_count", self._options_dist_models[0].as_float)
        if self._options_dist_models[1].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/y_dist_count", self._options_dist_models[1].as_float)
        if self._options_dist_models[2].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/z_dist_count", self._options_dist_models[2].as_float)            
        if self._options_random_models[0].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/x_random_count", self._options_random_models[0].as_float)
        if self._options_random_models[1].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/y_random_count", self._options_random_models[1].as_float)
        if self._options_random_models[2].as_float >= 0:
            settings.set("/persistent/exts/meta.cloud.explorer.azure/z_random_count", self._options_random_models[2].as_float)                        

        # #Serailize dictionaries
        # pickle.dump(self._aad_count, open('aad_count', 'w'))
        # pickle.dump(self._subscription_count, open('subscription_count', 'w'))
        # pickle.dump(self._location_count, open('location_count', 'w'))
        # pickle.dump(self._group_count, open('group_count', 'w'))
        # pickle.dump(self._type_count, open('type_count', 'w'))
        # pickle.dump(self._tag_count, open('tag_count', 'w'))

        # #aggregated data (costs)
        # pickle.dump(self._aad_cost, open('aad_count', 'w'))
        # pickle.dump(self._subscription_cost, open('subscription_cost', 'w'))
        # pickle.dump(self._location_cost, open('location_cost', 'w'))
        # pickle.dump(self._group_cost, open('group_cost', 'w'))
        # pickle.dump(self._type_cost, open('type_cost', 'w'))
        # pickle.dump(self._tag_cost, open('tag_cost', 'w'))

        # #mapped resources (indexes)
        # pickle.dump(self._map_aad, open('map_aad', 'w'))
        # pickle.dump(self._map_subscription, open('map_subscription', 'w'))
        # pickle.dump(self._map_location, open('map_location', 'w'))
        # pickle.dump(self._map_group, open('map_group', 'w'))
        # pickle.dump(self._map_type, open('map_type', 'w'))
        # pickle.dump(self._map_tag, open('map_tag', 'w'))



    #Load Saved config data                        
    def Load_Config_Data(self):
        settings = carb.settings.get_settings()
        self._rg_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rg_csv_file_path")
        self._rs_csv_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/rs_csv_file_path")
        self._azure_tenant_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_tenant_id")
        self._azure_client_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_client_id")
        self._azure_subscription_id = settings.get("/persistent/exts/meta.cloud.explorer.azure/azure_subscription_id")
        self._source_of_data = settings.get("/persistent/exts/meta.cloud.explorer.azure/last_data_source")
        self._bgl_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/bgl_file_path")
        self._bgm_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/bgm_file_path")
        self._bgh_file_path = settings.get("/persistent/exts/meta.cloud.explorer.azure/bgh_file_path")
        self._last_view_type= settings.get("/persistent/exts/meta.cloud.explorer.azure/last_view_type")

        try:
            self._options_count_models[0].set_value(int(settings.get("/persistent/exts/meta.cloud.explorer.azure/x_group_count")))
            self._options_count_models[1].set_value(int(settings.get("/persistent/exts/meta.cloud.explorer.azure/y_group_count")))
            self._options_count_models[2].set_value(int(settings.get("/persistent/exts/meta.cloud.explorer.azure/z_group_count")))
            self._options_dist_models[0].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/x_dist_count")))
            self._options_dist_models[1].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/y_dist_count")))
            self._options_dist_models[2].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/z_dist_count")))
            self._options_random_models[0].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/x_random_count")))
            self._options_random_models[1].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/y_random_count")))
            self._options_random_models[2].set_value(float(settings.get("/persistent/exts/meta.cloud.explorer.azure/z_random_count")))
        except: #set dfeualts
            self._composition_scale_model.set_value(1.0)
            self._options_count_models[0].set_value(10)
            self._options_count_models[1].set_value(10)
            self._options_count_models[2].set_value(1)
            self._options_dist_models[0].set_value(250)
            self._options_dist_models[1].set_value(250)
            self._options_dist_models[2].set_value(250)
            self._options_random_models[0].set_value(1.0)
            self._options_random_models[1].set_value(1.0)
            self._options_random_models[2].set_value(1)

        # #Reload dictionaries
        # self._aad_count = pickle.load(open('aad_count', 'r'))
        # self._subscription_count = pickle.load(open('subscription_count', 'r'))
        # self._location_count = pickle.load(open('location_count', 'r'))
        # self._group_count = pickle.load(open('group_count', 'r'))
        # self._type_count = pickle.load(open('type_count', 'r'))
        # self._tag_count = pickle.load(open('tag_count', 'r'))

        # #aggregated data (costs)
        # self._aad_cost = pickle.load(open('aad_cost', 'r'))
        # self._subscription_cost = pickle.load(open('subscription_cost', 'r'))
        # self._location_cost = pickle.load(open('location_cost', 'r'))
        # self._group_cost = pickle.load(open('group_cost', 'r'))
        # self._type_cost = pickle.load(open('type_cost', 'r'))
        # self._tag_cost = pickle.load(open('tag_cost', 'r'))

        # #mapped resources (indexes)
        # self._map_aad = pickle.load(open('map_aad', 'r'))
        # self._map_subscription = pickle.load(open('map_subscription', 'r'))
        # self._map_location = pickle.load(open('map_location', 'r'))
        # self._map_group = pickle.load(open('map_group', 'r'))
        # self._map_type = pickle.load(open('map_type', 'r'))
        # self._map_tag = pickle.load(open('map_tag', 'r'))

#-- SINGLETON SUPPORT
#-- SINGLETON SUPPORT

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
