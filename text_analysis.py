"""CLasses and function for analysis of any pdf document"""
# python imports
import time
import logging

# third party imports
import boto3

logger_access = logging.getLogger("gunicorn.access")
logger_error = logging.getLogger("gunicorn.error")

class DocumentAnalysis:
    """Get text from pdf files"""

    def __init__(self, s3bucket, object_name):
        self.s3_bucket_name = s3bucket
        self.object_name = object_name
        self.client = boto3.client('textract')

    def start_job(self):
        """To Start the document analysis"""
        response = self.client.start_document_analysis(
            DocumentLocation={
                'S3Object': {
                    'Bucket': self.s3_bucket_name,
                    'Name': self.object_name
                }
            },
            FeatureTypes=['FORMS'])
        return response["JobId"]

    def is_job_complete(self, job_id):
        """To check the status of document analysis"""
        time.sleep(5)
        response = self.client.get_document_analysis(JobId=job_id)
        logger_access.info("response: %s",response)
        status = response["JobStatus"]

        while status == "IN_PROGRESS":
            time.sleep(5)
            response = self.client.get_document_analysis(JobId=job_id)
            logger_access.info("response: %s",response)
            status = response["JobStatus"]
            logger_access.info("Job status: %s", status)
        return status

    def get_job_results(self, job_id):
        """To get response from analysis"""
        pages = []
        time.sleep(5)
        response = self.client.get_document_analysis(JobId=job_id)
        logger_access.info("response: %s", response)
        pages.append(response)
        # print("Result set page received: {}".format(len(pages)))
        next_token = None
        if 'NextToken' in response:
            next_token = response['NextToken']
        while next_token:
            time.sleep(5)

            response = self.client.get_document_analysis(JobId=job_id, NextToken=next_token)
            pages.append(response)
            # print('Result set page received: {}'.format(len(pages)))
            next_token = None
            if 'NextToken' in response:
                next_token = response['NextToken']
        return pages

    @staticmethod
    def get_kv_map(response):
        """get key and value maps"""

        key_map = {}
        value_map = {}
        block_map = {}
        text = ""
        logger_access.info("response: %s", response)
        for result_page in response:
            for block in result_page["Blocks"]:
                block_id = block['Id']
                block_map[block_id] = block
                if block["BlockType"] == "KEY_VALUE_SET":
                    if 'KEY' in block['EntityTypes']:
                        key_map[block_id] = block
                    else:
                        value_map[block_id] = block
                elif block["BlockType"] == "LINE":
                    text = text + '\n' + block["Text"]
        return key_map, value_map, block_map, text

    def get_kv_relationship(self, key_map, value_map, block_map):
        """Identify key value relationship"""
        kvs = {}
        logger_access.debug("key_map: %s , value_map: %s", key_map, value_map)
        logger_access.debug("block_map: %s", block_map)
        for key_block in key_map.items():
            value_block = self.find_value_block(key_block, value_map)
            logger_access.debug("key_block: %s, value_block: %s",key_block, value_block)
            key = self.get_text(key_block, block_map)
            val = self.get_text(value_block, block_map)
            kvs[key] = val
        return kvs

    @staticmethod
    def find_value_block(key_block, value_map):
        """Find the value of a key"""
        if isinstance(key_block,tuple):
            key_block = key_block[1]
        logger_access.debug("key_block: %s, value_map: %s", key_block,value_map)
        for relationship in key_block['Relationships']:
            logger_access.debug("Relationship is : %s", relationship)
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = value_map[value_id]
        return value_block

    @staticmethod
    def get_text(result, blocks_map):
        """Get text from the response"""
        text = ''
        if 'Relationships' in result:
            for relationship in result['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            text += word['Text'] + ' '
                        if word['BlockType'] == 'SELECTION_ELEMENT':
                            if word['SelectionStatus'] == 'SELECTED':
                                text += 'X '
        return text
