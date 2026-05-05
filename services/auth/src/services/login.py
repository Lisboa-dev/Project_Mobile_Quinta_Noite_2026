import bcrypt
from httpx import AsyncClient
import httpx
from .tokenJwt import TokenService 
from bcrypt import check_password_hash



userClient = AsyncClient(
    timeout=5.0,
    limits=httpx.Limits(
        max_connections=1000,
        max_keepalive_connections=100
    ),
    http2=True
)



userClient.base_url = "http://user-service:3000/"



def loginService(password: str, email: str='', name: str=''):

   if(email==''  and name==''):
       raise ValueError(" valores invalidos")
   
   if(email=='' and name!='' ):
       user = userClient.get("/users/", params={"name": name})
       if not user:
            raise ValueError(" valores invalidos")

   if(email!='' and name=='' and password!=''):
        user = userClient.get("/users/", params={"email": email})
        if not user:
            raise ValueError(" valores invalidos")
        
   is_valid = validate_password(password, user.password)
   if not is_valid:
            return None
        
   token = TokenService.generate_token(user.id)
   
   if not token:
            return None

   return {id:user.id, token: token}
    
  
  
  
  
  
def validate_password(password: str, hashed_password: str) -> bool:
    
   check = bcrypt.checkpw((password).encode('utf-8'), hashed_password.strip())
    
   if check:
        return True
   return False
