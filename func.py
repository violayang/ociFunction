import io
import os
import json
import xmltodict
import oci
from fdk import response
import cx_Oracle
import time
import psutil

os.environ['TZ'] = 'US/Eastern'
time.tzset()
fmt = '%Y-%m-%d %H:%M:%S'
start_time = time.strftime(fmt)



def handler(ctx, data: io.BytesIO=None):
    start = time.time()
    # -------------------- resource principals signer -------------------
    signer = oci.auth.signers.get_resource_principals_signer()
    os_client = oci.object_storage.ObjectStorageClient({}, signer=signer)

    # -------------------- extract oci resources metadata from Event message -------------------
    message = json.loads(data.getvalue())
    bucket_name = message['data']['additionalDetails']['bucketName']
    file_name = message['data']['resourceName']

    try:
        object = get_object(os_client, bucket_name, file_name)
        dic = xml_to_dict(object)
        sqlCommand = sql_command(dic)
        get_value_end = time.time()
        resp = '\nProcess xml file: ' + str(file_name) + '\nFunction start time: ' + start_time + '\nExtracting values execution time: ' + str(get_value_end - start) + 'seconds\n'

        # -------------------- DB connection -------------------
        db_con_start = time.time()
        conn = db_connection(os_client)
        # -------------------- SQL execution -------------------
        db_exe_start = time.time()
        db_execution(conn, sqlCommand)

        resp += 'DB connection building: ' + str(
            db_exe_start - db_con_start) + 'seconds\n' + 'DE execution time: ' + str(
            time.time() - db_exe_start) + 'seconds\n' + check_RAM()

    except (Exception, ValueError) as ex:
        resp = str(ex)

    return response.Response(
        ctx,
        response_data=put_object(os_client, str(resp), file_name),
        headers={"Content-Type": "application/json"}
    )



def get_object(os_client, bucket_name, object_name):
    namespace = os_client.get_namespace().data
    response = os_client.get_object(namespace_name=namespace, bucket_name=bucket_name, object_name=object_name)
    return response.data.raw.data


def xml_to_dict(xml_text):
    ordered_dict = xmltodict.parse(xml_text.decode('utf-8'))
    return ordered_dict


def sql_command(dic):
    response = []

    ## -----------------------------------------------------------------------------
    ##                          Data Transformation
    ## -----------------------------------------------------------------------------

    return response




def db_connection(os_client):
    file = get_object(os_client, "<bucket_name>", "<object_name>") ## replace bucket and object
    conn = json.loads(file)
    user = str(conn['user'])
    password = str(conn['password'])
    dsn = str(conn['dsn'])
    connection = cx_Oracle.connect(user, password, dsn, cclass="PYCLASS", purity=cx_Oracle.ATTR_PURITY_SELF) ## DRCP
    return connection


def db_execution(connection, sql_command):  ## parse sql_command: list
    cursor = connection.cursor()
    # ---------------------- SQL execution ----------------------------
    for i in sql_command:
        cursor.execute(i)

    ## --------------------- ADD: insert datastamp in log table --------------------
    ##          here
    ## -----------------------------------------------------------------------------
    connection.commit()
    connection.close()
    return


def put_object(os_client, txt, fileName):
    namespace = os_client.get_namespace().data
    bucket_name = "<bucketName>"  ## replace bucketName
    file_name = time.strftime(fmt) + str(fileName) + '.txt'
    response = os_client.put_object(namespace_name=namespace, bucket_name=bucket_name, object_name=file_name,
                                    put_object_body=txt)
    return response


# ---------------------- check RAM usage ----------------------------
def check_RAM():
    pid = os.getpid()
    py = psutil.Process(pid)
    memoryUse = float(py.memory_info()[0] / (1000 * 1000))  # MB
    response = '\nrrs memory use: ' + str(memoryUse)
    return response

