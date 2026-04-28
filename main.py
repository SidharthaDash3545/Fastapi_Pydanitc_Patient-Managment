from fastapi import FastAPI ,Path, HTTPException ,Query
from fastapi.responses import JSONResponse
# HTTP Expcetion is used to handel the error in the api and return the appropriate response to the client 
# A proper Http sts code is 404, 400,403) ets
from pydantic import BaseModel,Field,computed_field
from typing import Annotated,Literal,Optional
import json
app = FastAPI() 
class Patient(BaseModel):
     id:Annotated[str,Field(...,description='ID of the patient',example='P001')]
     name:Annotated[str,Field(...,description='Name of the patient')]
     city:Annotated[str,Field(...,description='City of the patient')]
     age:Annotated[int,Field(...,description='Age of the patient')]
     gender:Annotated[Literal['male','female','other'],Field(...,description='Gender of the patient')]
     height:Annotated[float,Field(...,gt=0, description='Height of the patient in mtrs')]
     weight:Annotated[float,Field(...,gt=0, description='Weight of the patient in kgs')]

     @computed_field
     @property
     def bmi(self) -> float:
          bmi = round(self.weight/(self.height**2),2)
          return bmi
     
     @computed_field
     @property
     def vardict(self) -> str:
          
          if self.bmi <18.5:
               return 'underWeight'
          elif self.bmi< 25:
               return 'normal'
          elif self.bmi <30:
               return 'normal'
          else:
               return 'obese'
class Patientupdate(BaseModel):
     name:Annotated[Optional[str],Field(default=None)]
     city:Annotated[Optional[str],Field(default=None)]
     age:Annotated[Optional[int],Field(default=None)]
     gender:Annotated[Optional[Literal['male','female']],Field(default=None)]
     height:Annotated[Optional[float],Field(default=None,gt=0)]
     weight:Annotated[Optional[float],Field(default=None,gt=0)]
             

def load_data():
    with open('patients.json','r') as file:
        data = json.load(file)

    return data  

def save_data(data):
     with open ('patients.json','w')as file:
          json.dump(data,file)
     

@app.get('/')
def hello():
    return {'message':'Patient Management System API'}

@app.get('/about')
def about():
    return{'about':'A fully functional Api to manage your patient rocords'}

@app.get('/view')
def view_patients():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id:str = Path(..., description = "ID of the patient in the database",example = "P001")):
    # load all  The patient
    data = load_data()
    # check if the patient id exists in the data
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code = 404 ,detail= 'patient not found' ) 

@app.get('/sort')
def sort_patients(sort_by: str = Query(...,description='sort on the basic of height ,weight or bmi'),order:str = Query('asc',description ='sort oder can be asc or desc')):
        data = load_data() # load all data
        if sort_by not in ['height', 'weight', 'bmi']:
             raise HTTPException(status_code=400, detail='invalid sort_by parameter. Must be one of height, weight or bmi')
        if order not in ['asc', 'desc']:
             raise HTTPException(status_code=400, detail='invalid order parmeter.Must be one of asc or desc')
        sorted_data = sorted(data.values(), key=lambda x: x[sort_by], reverse=(order == 'desc'))
        return sorted_data

@app.post('/create')
def create_patient(patient: Patient):
    data = load_data() # load Existing data
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')# check if patinet alredy exsist
    data[patient.id] = patient.model_dump(exclude={'id'})#add newe patient to ths data
    save_data(data) # save the data to the file
    return JSONResponse(status_code=201,content={'message':'patinet created successfully'})


@app.put('/edit/{patient_id}')
def update_patient(patient_id:str,patient_update:Patientupdate):
     data =  load_data()# loAD EXSINTING DATA
     if patient_id not in data:
          raise HTTPException(status_code=404,detail='patinet not found')
     existing_patient_info =  data[patient_id]
     update_patient_info= patient_update.model_dump(exclude_unset=True)
     for key, value in update_patient_info.items():
          existing_patient_info[key] = value

     #existing_patient_info -> pydantic object ->update bmi +verdict
     existing_patient_info['id'] = patient_id
     Patient_pydantic_obj=Patient(**existing_patient_info)
     #pydantic object -> dict
     existing_patient_info = Patient_pydantic_obj.model_dump(exclude='id')

     # add this dict to data
     data[patient_id]= existing_patient_info
     save_data(data) # save the data to the file
     return JSONResponse(status_code=200,content={'message': 'patient updated'})


@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str  ):
     data = load_data()
     if patient_id not in data:
          raise HTTPException(status_code=404,detail='patinet not found')
     del data[patient_id]
     save_data(data)
     return JSONResponse(status_code=200,content={'message': 'patient deleted'})
    

