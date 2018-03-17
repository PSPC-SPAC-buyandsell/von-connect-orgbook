from app import app
from app.services import issuer

#
# Copyright 2017-2018 Government of Canada - Public Services and Procurement Canada - buyandsell.gc.ca
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import asyncio
import logging
from sanic import response
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'HEAD'])
def index(request):
    return response.file('index.html')

@app.route('/health', methods=['GET', 'HEAD'])
async def health(request):
    ready = await app.issuer_endp.request('ready')
    return response.text('ok' if ready else '', status=200 if ready else 451)

@app.route('/status', methods=['GET', 'HEAD'])
async def status(request):
    #status = app.exchange.status()
    status = await app.issuer_endp.request('status')
    return response.json(status)

# Corresponds with testing code in app/__init__.py
#@app.route('/hello', methods=['GET', 'HEAD'])
#async def hello(request):
#    hello = app.executor.get_endpoint('hello', True)
#    result = await hello.request('isthereanybodyoutthere')
#    return response.json(result)

@app.route('/submit_claim', methods=['POST'])
async def submit_claim(request):
    schema_name = request.raw_args.get('schema')
    schema_version = request.raw_args.get('version') or None
    if not schema_name:
        return response.text("Missing 'schema' parameter", status=400)
    if not request.json:
        return response.text(
            'Request body must contain the schema attributes as a JSON object',
            status=400)
    try:
        result = await app.issuer_endp.request(
            issuer.SubmitClaimRequest(schema_name, schema_version, request.json))
        if isinstance(result, issuer.SubmitClaimResponse):
            ret = {'success': True, 'result': result.value}
        elif isinstance(result, issuer.IssuerError):
            ret = {'success': False, 'result': result.value}
        else:
            raise ValueError('Unexpected result from issuer')
    except Exception as e:
        logger.exception('Error while submitting claim')
        ret = {'success': False, 'result': str(e)}
    return response.json(ret)

