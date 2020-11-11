from app import db
from flask import render_template,request,jsonify,make_response
from sqlalchemy import desc,or_
from functools import wraps
from sqlalchemy.inspection import inspect
import os

def post_id_validation(req,cls,field=None,order=None):
    id = req.form.get("id")
    xstr = lambda s: s or ""

    if id is None:return (False,("id must be sent!",500))

    if field is None:
        en = cls.query.get(str(id))
    else:
        field = getattr(cls,field).like("%{}%".format(str(id)))
        en = cls.query.filter(field).order_by(order).all()
    
    if en: return True,en

    return (False,("id not found!",500))

def get_id_validation(req,cls,field=None,order=None):
    id = req.args.get("id")
    xstr = lambda s: s or ""
    content = xstr(req.headers.get("Content-Type"))

    if id is None:return (False,("id must be sent!",500) if "json" in content else render_template("grafana1.html",value="id must be sent!",color=False))

    if field is None:
        en = cls.query.get(str(id))
    else:
        field = getattr(cls,field).like("%{}%".format(str(id)))
        en = cls.query.filter(field).order_by(order).all()
    
    if en: return True,en,content

    return (False,("id not found!",500) if "json" in content else render_template("grafana1.html",value="id not found!",color=False))


def validate_field2(cls,value,like=None,field=None,order=None):
    #xstr = lambda s: s or ""
    #contentJson = "json" in xstr(request.headers.get("Content-Type"))

    if field is None:
        en = cls.query.get(str(value))
        field = inspect(cls).primary_key[0].name
    else:
        value = value if not like else like.format(value)
        _field = getattr(cls,field).like(value)
        en = cls.query.filter(_field).order_by(order).all()

    return en,"OK" if en else "couldn't find '{}' value at '{}' column".format(value,field)

def retContent(value,jsn,error=False):
    xstr = lambda s: s or ""
    contentJson = "json" in xstr(request.headers.get("Content-Type"))
    return jsn if contentJson else render_template("grafana1.html",value=value,color=error)

#decorator

def fields_required(lista,methods="*",out="fields"):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            xstr = lambda s: s or ""
            contentJson = "json" in xstr(request.headers.get("Content-Type"))

            if methods == "*" or request.method in methods:
                if request.method == "GET":
                    fields = request.args.to_dict()
                elif request.method in ["POST","PUT","DELETE","DEL","CREDIT"]:
                    data = request.get_json(force=True) or request.get_json() or request.form.to_dict()
                    fields =  request.json if contentJson else data
                
                lista2 = lista if isinstance(lista,list) else list(lista.keys())

                notfound = [x for x in lista2 if not x in fields]
                if notfound:
                    return "campos nao encontrados!:\n\t" + "\n\t".join(notfound),400
                
                if isinstance(lista,dict):
                    for k,v in lista.items():
                        
                        if v == float and isinstance(fields[k],int):
                            fields[k] = float(fields[k])

                        if not isinstance(fields[k],v):
                            tipo = str(v).split("'")[1]
                            return f"o campo '{k}' nao corresponde ao tipo ({tipo})",400


                kwargs[out] = fields
                result = function(*args, **kwargs)
                return result
            else:
                kwargs[out] = []
                return function(*args, **kwargs)

        return wrapper
    return decorator


def validate_field(cls,value,like=None,field=None,order=None,fixedjson=None,errorMsg=None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            _value = kwargs['fields'][value]
            if field is None:
                en = cls.query.get(str(_value))
                fieldName = inspect(cls).primary_key[0].name
            else:
                _value = _value if not like else like.format(_value)
                _field = getattr(cls,field).like(_value)
                en = cls.query.filter(_field).order_by(order).all()
                fieldName = field

            falseValue = errorMsg if errorMsg else "couldn't find '{}' value at '{}' column".format(_value,fieldName)

            if not en: return falseValue if fixedjson else retContent(falseValue,falseValue,False)
            return function(en,*args, **kwargs)
        return wrapper
    return decorator


#===================================REDUCE IMAGES#
from PIL import Image

def reduceSave(img,local):
    Image.open(img).save(local,quality=80)

def deleteImage(img):
    os.remove(img, dir_fd=None)

