# coding=utf-8
'''
Created on Jun 10, 2015

@author: xuliyan; Yufeng Chen
'''


import math
import random
import arcpy
from arcpy import env
from arcpy.sa import *
import numpy as np
from random import choice

class Energy(object):
    '''
    The Energy Class.
    '''


    def __init__(self):
        '''
        '''
        self.hh_energy_type = 0
        
        self.energy_demand = 0
        self.electricity_consumption = 0
        self.firewood_consumption = 0
        self.firewood_consumption_in_kwh = 0
        self.carbon_footprint = 0


    def energy_step_go(self, hh, model_parameters):

        self.get_household_energy_type(hh, model_parameters)
        self.get_energy_demand(hh, model_parameters)
        self.get_electricity_consumption(hh, model_parameters)
        self.get_firewood_consumption(hh, model_parameters)

        self.get_carbon_footprint(hh, model_parameters)


    
    
    def get_household_energy_type(self, hh, model_parameters):
        
        if hh.business_type == 0:
            self.hh_energy_type = 1
            
        elif hh.business_type == 1:
            self.hh_energy_type = 2
        
        else:
            self.hh_energy_type = 3
    
    
    
    
    def get_energy_demand(self, hh, model_parameters):
        
        self.energy_demand = math.exp ((6.069 + 0.205 * self.hh_energy_type + 0.05 * hh.own_capital_properties.hh_size + 
                                  0.009 * hh.own_capital_properties.house_rooms)) / 0.18
        


    
    
    def get_electricity_consumption(self, hh, model_parameters):
        
        # If the household has engaged in the lodging business
        is_lodging = int()
        
        if hh.own_capital_properties.lodging_income != 0:
            is_lodging = 1
        else:
            is_lodging = 0
        
        # Calculate potential electricity demand
        potential_elec_demand = math.exp ((5.684 + 0.216 * self.hh_energy_type + 0.072 * hh.own_capital_properties.hh_size +
                                     0.447 * is_lodging)) / float(model_parameters['ElectricitySubsidisedPrice'])
        
        # Get the actual electricity consumption
        if potential_elec_demand <= self.energy_demand:
            self.electricity_consumption = potential_elec_demand
        else:
            self.electricity_consumption = self.energy_demand
                
    
    
    def get_firewood_consumption(self, hh, model_parameters):
        
        self.firewood_consumption = (self.energy_demand - self.electricity_consumption) * float(model_parameters['ElectricityToFirewoodRatio'])
        self.firewood_consumption_in_kwh = self.energy_demand - self.electricity_consumption

    
    
    def get_carbon_footprint(self, hh, model_parameters):
        
        self.carbon_footprint = (self.electricity_consumption * float(model_parameters['ElectricityToCarbon']) + 
                                 self.firewood_consumption * float(model_parameters['FirewoodToCarbon']))

    def get_firewood_collection_area(self, woodneed, currentyear, iterationcount):


        env.workspace = "C:/WolongRun/Results_Output/linshi"
        arcpy.CheckOutExtension("Spatial")
        # Get input Raster properties
        arcpy.env.overwriteOutput = True

        if iterationcount == 0:
            resource = arcpy.Raster('C:\WolongRun\Results_Output\linshi\wood.tif')
            habitat = arcpy.Raster('C:\WolongRun\Results_Output\linshi\habitat.tif')
        else:
            woodpath = "C:/WolongRun/Results_Output/energy/wood" + '_' + str(iterationcount)+ '.tif'
            resource = arcpy.Raster(woodpath)
            habitatpath = "C:/WolongRun/Results_Output/energy/habitat" + '_' + str(iterationcount)+ '.tif'
            habitat = arcpy.Raster(habitatpath)
        costRaster = arcpy.Raster('C:\WolongRun\Results_Output\linshi\cosdis.tif')
        original = arcpy.Raster('C:\WolongRun\Results_Output\linshi\groups.tif')



        dsc = arcpy.Describe(habitat)
        arcpy.env.outputCoordinateSystem = dsc.SpatialReference

        lowerLeft = arcpy.Point(habitat.extent.XMin,habitat.extent.YMin)
        cellSize = habitat.meanCellWidth

        # Convert Raster to numpy array
        B_arr = arcpy.RasterToNumPyArray(original, nodata_to_value=0)  # 居民点（0，1）
        R_arr = arcpy.RasterToNumPyArray(resource, nodata_to_value=0)  # 储量矩阵（）
        C_arr = arcpy.RasterToNumPyArray(costRaster, nodata_to_value=0)
        h_arr = arcpy.RasterToNumPyArray(habitat,nodata_to_value=0)


        inZoneData = "fishnet.shp"
        zoneField = "OBJECTID"
        inValueRaster = "wood.tif"
        outZonalStatistics = ZonalStatistics(inZoneData, zoneField, inValueRaster,
                                             "MEAN", "NODATA")
        X_arr = arcpy.RasterToNumPyArray(outZonalStatistics, nodata_to_value=0)
        # check
        # print(B_arr,W_arr)
        # initial
        born = np.array(np.where(B_arr == 1))
        num = born.shape[1]
        # print(O_arr)
        Bornpixel = born.T.tolist()

        # 寻柴者

        self.path = []
        self.collect = []
        A_arr = R_arr.copy()
        Y_arr = X_arr.copy()
        for number in range(num):
            path_mat = []
            collect_mat = []
            born = []
            visit0, visit1 = Bornpixel[number]  # 初始化出生点
            born.extend([visit0, visit1])
            collected_wood = 0  # 捡柴量为0
            path_mat.append(born)  # 单次路径加上起点
            while Y_arr[visit0][visit1] < 300:
                unvisit_list = [[visit0 - 1, visit1 - 1], [visit0, visit1 - 1],
                                [visit0 + 1, visit1 - 1], [visit0 - 1, visit1],
                                [visit0 + 1, visit1], [visit0 - 1, visit1 + 1],
                                [visit0, visit1 + 1], [visit0 + 1, visit1 + 1]]
                trans_list = []
                nextstep = []
                for k in range(8):  # 轮盘赌
                    a, b = unvisit_list[k]
                    if (k == 0 or k == 2 or k == 5 or k == 7):
                        trans = (C_arr[a][b] + C_arr[visit0][visit1]) / 2
                    if (k == 1 or k == 3 or k == 4 or k == 6):
                        trans = math.sqrt(2) * (C_arr[a][b] + C_arr[visit0][visit1]) / 2
                    trans_list.append(trans)
                total = sum(trans_list)
                for i in range(8):
                    trans_list[i] = trans_list[i] / total
                prob = 0
                ran = random.uniform(0, 1)
                for t in range(8):
                    prob += trans_list[t]
                    if ran < prob:
                        if random.uniform(0, 0.1) < 0.08:
                            x, y = unvisit_list[t]
                            visit0, visit1 = x, y
                            break
                        else:
                            continue

                nextstep.extend([visit0, visit1])
                path_mat.append(nextstep)


            while collected_wood < woodneed:
                nextstep1 = []
                collected_wood += R_arr[visit0][visit1]
                R_arr[visit0][visit1] = 0
                x_step = choice([1, 0, -1])
                y_step = choice([1, 0, -1])
                visit0 += x_step
                visit1 += y_step
                nextstep1.extend([visit0, visit1])
                collect_mat.append(nextstep1)
            self.path.append(path_mat)
            self.collect.append(collect_mat)

        p_arr = np.zeros(np.shape(h_arr))
        for i in range(len(self.path)):
            for c,r in self.path[i]:
                p_arr[c][r] = 1


        pa = arcpy.NumPyArrayToRaster(p_arr, lowerLeft, cellSize, value_to_nodata=0)
        energy_path = "C:/WolongRun/Results_Output/energy/"
        ener_save_year = currentyear
        energyout = energy_path + 'Path' + '_' + str(ener_save_year) + '.tif'
        pa.save(energyout)

        q_arr = np.zeros(np.shape(h_arr))
        for j in range(len(self.collect)):
            for c, r in self.collect[j]:
                q_arr[c][r] = 1

        qa = arcpy.NumPyArrayToRaster(q_arr, lowerLeft, cellSize, value_to_nodata=0)
        collectout = energy_path + 'collect' + '_' + str(ener_save_year) + '.tif'
        qa.save(collectout)

        inRaster = arcpy.Raster(collectout)
        outPoint = energy_path + 'collect_point' + '_' + str(ener_save_year) + '.shp'
        arcpy.RasterToPoint_conversion(inRaster, outPoint, "VALUE")


        woodout = energy_path + 'wood' + '_' + str(iterationcount + 1) + '.tif'
        Rsr = arcpy.NumPyArrayToRaster(R_arr, lowerLeft, cellSize, value_to_nodata=0)
        Rsr.save(woodout)

        total = q_arr * random.randint(1,15)
        Final = h_arr - total
        habitatout = energy_path + 'habitat' + '_' + str(iterationcount + 1)+ '.tif'
        ta = arcpy.NumPyArrayToRaster(Final, lowerLeft, cellSize, value_to_nodata=0)
        ta.save(habitatout)

        # kernel = KernelDensity('collect_point' + '_' + str(ener_save_year) + '.shp', "NONE", 45, 1200, "SQUARE_KILOMETERS")
        #
        # outkernel = energy_path + 'kernel' + '_' + str(ener_save_year) + '.tif'
        # kernel.save(outkernel)







    
    
    
    
    
    
    
    
    
    
    