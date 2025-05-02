class DigiProdEvents:
    def __init__(self, digiprod_events) -> None:
        self.digiprod_events = digiprod_events

    def get_machine_name(self):
        return self.digiprod_events.get("machine_name", "NA")

    def is_downtime_detected(self):
        return self.digiprod_events.get("downtime_start_detected", False)
    
    def is_downtime_over(self):
        return self.digiprod_events.get("downtime_end_detected", False)
    
    def get_downtime_reason_tag(self):
        return self.digiprod_events.get("downtime_start_detected",{}).get("reason","NA")

    def is_batch_change_detected(self):
        return self.digiprod_events.get("batch_change_detected", False)

    def get_program_number(self):
        program_number = (self.digiprod_events.get("station_1_counter", {}).get("program_number", None) or
                self.digiprod_events.get("station_2_counter", {}).get("program_number", None) or
                self.digiprod_events.get("batch_change_detected", {}).get("program_number", None)
                )

        if program_number:
            return str(program_number)
    
    def get_station_1_counter(self):
        return self.digiprod_events.get("station_1_counter", None)
    
    def get_station_2_counter(self):
        return self.digiprod_events.get("station_2_counter", None)
    
    def get_output_change(self):
        return self.digiprod_events.get("output_material_change", None)
    
    def get_station_2_counter(self):
        return self.digiprod_events.get("station_2_counter", None)
    
    def get_SPM(self):
        return self.digiprod_events.get("SPM", None)

    def get_SPM_avg(self):
        return self.digiprod_events.get("spm_avg_update", None)

    def get_shop_id(self):
        return int(self.digiprod_events["shop_id"])




