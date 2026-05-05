from ..Interfaces.UseCasesUserInterface import IUseCasesCreateUser, IUseCasesDetailUser, IUseCasesListUser, IUseCasesDeleteUser, IUseCasesUpdateUser
from fastapi import APIRouter, Depends
from ..provider import UserFactory




routerUsers = APIRouter(
    prefix="/user", 
    tags=["uaser"],
    #dependencies= Depends(hookFunction)
)


@routerUsers.post(
        "/",
        #dependencies= Depends(hookFunction)
    )

def create_User(self, name: str,  useCase: IUseCasesCreateUser = Depends(UserFactory.useCaseCreateUser_factory)):
        return useCase.execute(name)
    



@routerUsers.put(
        "/",
        #dependencies= Depends(hookFunction)
    )
def update_User(self, name: str,  useCase: IUseCasesUpdateUser = Depends(UserFactory.useCaseUpdateUser_factory)):
        return useCase.execute(name)
    
    
    



@routerUsers.delete(
        "/",
        #dependencies= Depends(hookFunction)
    )
def delete_User(self, name: str,  useCase: IUseCasesDeleteUser = Depends(UserFactory.useCaseDeleteUser_factory)):
        return useCase.execute(name)
    



@routerUsers.get(
        "/",
        #dependencies= Depends(hookFunction)
    )
def list_User(self, name: str,  useCase: IUseCasesListUser = Depends(UserFactory.useCaseListUser_factory)):
            return useCase.execute(name)
    


@routerUsers.get(
        "/{userId}",
        #dependencies= Depends(hookFunction)
    )
def detail_User(self, name: str,  useCase: IUseCasesDetailUser = Depends(UserFactory.useCaseDetailUser_factory)):
            return useCase.execute(name)
    

@routerUsers.post(
        "/",
        #dependencies= Depends(hookFunction)
    )

def get_user_by_email_or_userName(value: str, useCase: IUseCasesDetailUser = Depends(UserFactory.useCaseAuthUser_factory)):

    useCase.execute(value)
'''
 retur to {
     "id": 1,
     "name": "string",
     "password": "string",
     "uerName": "string",
     "role": "string",
     "cargo": "string"
 }
'''




    #admin metodes

    #super admin metodes