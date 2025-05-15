from ..repositories.msil_production_repository import MSILProductionRepository
from ..repositories.models.msil_production import MSILProduction
from ..repositories.models.msil_part import MSILPart
from ..repositories.msil_shift_repository import MSILShiftRepository
from .service import Service
import datetime
from .shift_util import get_shift, get_production_date
import pytz

ist_tz = pytz.timezone('Asia/Kolkata')
class MSILProductionService(Service):
    def __init__(self, repository : MSILProductionRepository, shift_repo: MSILShiftRepository):
        super().__init__(repository, self.transform_model_to_dict, 
                         self.transform_dict_to_model)
        self.repository = repository
        self.shift_repository = shift_repo
    
    def get_production_by_equipment_id(self, equipment_id):
        shift = get_shift(datetime.datetime.time(datetime.datetime.now(ist_tz)))
        today = get_production_date(shift)
        production = self.repository.get_production(equipment_id, today, shift)
        return self.transform_model_to_dict(production)
    
    def start_production(self, production_id, input_materials, output_parts, work_order_number_1, work_order_number_2=None, with_input=True):        
        self.repository.start_production(production_id,input_materials, output_parts, work_order_number_1, work_order_number_2, with_input)

    def update_SPM_avg(self, production_id,part_1, part_2, SPM_update):
        self.repository.update_SPM_avg(production_id,part_1, part_2, SPM_update)

    def start_batch(self, production_id, change_time, shop_id=None, shift=None):
        """
        Starts a batch process with the given parameters.

        Args:
            production_id (str): ID of the production record.
            change_time (int): Timestamp of the change.
            shop_id (int, optional): Shop ID (default: None).
            shift (str, optional): Shift ID (default: None).
        """
        dt_object = datetime.datetime.fromtimestamp(change_time, ist_tz).replace(tzinfo=None)
        return self.repository.start_batch(production_id, dt_object, shop_id, shift)


    def change_variant(self, production_id, material_code, prev_material_code, part, shop_id):
        self.repository.change_variant(production_id, material_code, prev_material_code, part, shop_id)

    def update_output(self, production_id,  material_code):
        self.repository.update_output(production_id, material_code)

    def update_program(self, production_id, change_time, output_parts, work_order_1, work_order_2, shop_id):
        dt_object = datetime.datetime.fromtimestamp(change_time, ist_tz).replace(tzinfo=None)
        return self.repository.update_program(production_id, dt_object, output_parts, work_order_1, work_order_2, shop_id)

    def update_downtime(self, production_id, is_down):
        self.repository.update_downtime(production_id, is_down)

    def transform_model_to_dict(self, model : MSILProduction):
        prod = {
            "id" : model.id,
            "machine_id" : model.equipment_id,
            "date" : model.date,
            "is_down" : model.is_down,
            "shift" : model.shift,
            "status" : None,
            "part_1" : model.part_1,
            "part_2" : model.part_2
        }
        if model.status != None:
            prod["status"] = model.status.name

        return prod

    def transform_dict_to_model(self, dict):
        pass

    def pause_production_status(self, production_id):
        result = self.repository.pause_production(production_id)

    def get_production_view_service(self, prodution_id, shop_id):
        first_shift_time = self.shift_repository.day_start_time(shop_id=shop_id)
        production_data = self.repository.get_production_view(first_shift_time,prodution_id, shop_id)
        processed_data = {
            'production': {},
            'parts': []
        }
        production_obj = production_data[0]
        production_dict = {
            'id': production_obj.id,
            'date': production_obj.date.strftime('%Y-%m-%d'),

        }
        processed_data['production'] = production_dict

        for part_data in production_data[1]:
            part_obj : MSILPart = part_data['part_obj']
            part_dict = {
                'part_obj': {
                    'material_code': part_obj.material_code,
                    'part_name': part_obj.part_name,
                    'pe_code' : part_obj.pe_code

                },
                'plan': part_data['plan'],
                'actual': part_data['actual'],
                'variant_list': part_data['variant_list'],
                'batch_list': [],
                'reject': part_data['reject'],
                'rework': part_data['rework'],
                'hold': part_data['hold'],
                'efficiency': round(float(part_data['efficiency']),2),
                'SPM': part_data['spm'],
                'model': part_data['model']
            }



            batch_list = []
            for batch_obj in part_data['batch_list']:
                batch_dict = {
                    'id' : batch_obj[0].id,
                    'batch_id': batch_obj[0].name,
                    'output_details' : batch_obj[0].output_id,
                    'start_time': batch_obj[0].start_time,
                    'end_time': batch_obj[0].end_time,
                    'SPM': batch_obj[1],
                    'prod_qty': batch_obj[2],
                    'reject_qty': batch_obj[3],
                    'rework_qty': batch_obj[4],
                    'hold_qty': batch_obj[5],
                    'input_details' : batch_obj[6],
                    'efficiency':round(float(batch_obj[7]),2)

                }
                batch_list.append(batch_dict)

            part_dict['batch_list'] = batch_list
            processed_data['parts'].append(part_dict)


        return processed_data
