from singular_pipe._types import HttpResponse
import json
from singular_pipe._types import InputFile
def cache_http(self,prefix,
	_res = HttpResponse('GET','http://dummy.restapiexample.com/api/v1/employees'),
	_output = ['cache',]
	):
	with open(self.output.cache,'w') as f: f.write(_res.text)
	return self

def parse_json(self,prefix,
	jsonFile = InputFile,
	_output = ['log'],
	):
	with open(jsonFile,'r') as f: 
		x = json.load(f)['data']
	with open(self.output.log,'w') as f:
		f.write('Average_salary:%.2f\n'%(sum( [int(xx['employee_salary']) for xx in x])/float(len(x))))
	return self

from singular_pipe.runner import force_run
if __name__ == '__main__':
	runner = force_run
	root = '/tmp/pipeline_download'
	curr = runner(cache_http, root,)
	curr = runner(parse_json, root, curr.output.cache, )
