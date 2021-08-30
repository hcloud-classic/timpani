import logging
import json

from marshmallow import ValidationError
from werkzeug.wrappers import Response
from ..gql_client.GqlClient import GqlClient

from timpani_gateway.exceptions import InvalidError
logger = logging.getLogger(__name__)

class DataParser(object):
    app = None

    def setapp(self, app):
        self.app = app

    def response_data(self, func):
        def decorator(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
                # print("response_data res : {}".format(res))
                # json_res = json.dumps(res)
                if 'errorcode' in res:
                    retMsg = {'result': res['errorcode'], 'resultMessage': res['errorstr'], 'resultData': {'page_msg' : res['page_msg']}}
                else:
                    retMsg = {'result': '0000', 'resultMessage': 'Success', 'resultData': res}
                json_res = json.dumps(retMsg, ensure_ascii=False).encode('utf-8')
            except AttributeError as exc:
                print("Exception {}".format(exc))
                raise InvalidError({'code': 'ATTRIBUTE_ERROR', 'message': '서비스를 찾을 수 없음'}, status_code=500)
            except KeyError as exc1:
                print("Exception {}".format(exc1))
                raise InvalidError({'code': 'KEY_ERROR', 'message': '매칭 키를 알 수 없음'}, status_code=500)
            except Exception as e:
                print("Exception {}".format(e))
                raise InvalidError("{'code':'ERROR_UNKNOWN','message':'알 수 없는 에러'}", status_code=500)

            return json_res

        return decorator

    def gqlclient(self, func):
        def decorator(*args, **kwargs):
            try:
                client = GqlClient("http://192.168.221.1:38080/graphql", self.app)
                kwargs['client'] = client
                kwargs['app'] = self.app
                res = func(*args, **kwargs)
            except Exception as e:
                logger.info("EXCEPTION : {}".format(e))
            return res
        return decorator

    def response_exception(self, err_code, err_dic):
        error_code_str = '0' + str(err_code)
        if type(err_dic).__name__.__eq__('NoneType'):
            retMsg = {'result': error_code_str, 'resultMessage': 'INTERNAL ERROR'}
        else:
            retMsg = {'result': error_code_str, 'resultMessage': 'Fail', 'resultData': err_dic}
        logger.info("[RESPONSE] : {}".format(retMsg))
        return Response(json.dumps(retMsg, ensure_ascii=False).encode('utf-8'), status=err_code)

    def response_success(self):
        print("[success] 200 OK")
        Response(status=200)

    def response_success_body(self, data_dic):
        if type(data_dic).__name__.__eq__('NoneType'):
            retMsg = {'result': '0000', 'resultMessage': 'Success'}
        else:
            retMsg = {'result': '0000', 'resultMessage': 'Success', 'resultData': data_dic}
        logger.info("[RESPONSE] : {}".format(retMsg))
        return Response(json.dumps(retMsg, ensure_ascii=False).encode('utf-8'), status=200)

    def GetJson(self, schemas, request):
        try:
            # JSON 문구 파싱 루틴
            if 'json' in request.form:           # multipart form-data
                json_str = request.form['json']
            else:
                json_str = request.get_data(as_text=True)
            req_data = schemas.loads(json_str).data
        except ValueError as exc:
            print("Exception {}".format(exc))
            raise InvalidError({'code':'PARAMETER_UNKNOWN','message':'파라미터 오류'},status_code=400)
        except ValidationError as exc:
            print("Exception {}".format(exc))
            raise InvalidError({'code':'PARAMETER_MISSING','message':'파라미터 없음'},status_code=400)
        except Exception as e:
            print("Exception {}".format(e))
            raise InvalidError({'code':'ERROR_UNKNOWN','message':'알 수 없는 에러'},status_code=400)
        return req_data

class EndpointAction(object):
    def __init__(self, action):
        self.action = action

    def __call__(self, *args, **kwargs):
        res = self.action(*args, **kwargs)
        logger.info("res : {}".format(res))
        return res
        # self.response = Response(res, status=200, headers={})
        # return self.response