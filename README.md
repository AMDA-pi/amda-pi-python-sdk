<!-- [<img src="https://www.amdapi.com/assets/logo-52efa03bae0cbae715588d415a3e3c8d4a1d50af9e24af99d7bb55d4b967738d.png">](https://www.amdapi.com/) -->

# AMDAPi Python SDK
![](https://img.shields.io/badge/python-3.8%2B-green)  
<br/>
<br/>
The AMDAPi Python SDK package serves as a native python interface allowing for easy consumption of AMDAPi API services.  
<br/>

----------------------------------------------------------------
<br/>

  - [**Installation**](#installation)
  - [**Quick-Start Guide**](#quick-start-guide)
    - [**Creating a Client**](#creating-a-client)
    - [**Analyzing a Call**](#analyzing-a-call)
      - [**Call Params**](#call-params)
      - [**Example**](#example)
    - [**Retrieving A Call**](#retrieving-a-call)
    - [**Searching for Multiple Calls**](#searching-for-multiple-calls)
      - [**Search params**](#search-params)
      - [**Default Search**](#default-search)
    - [**Deleting Calls**](#deleting-calls)
  - [**Reference Docs**](#reference-docs)
  
<br>

---------
## **Installation**
<br>

The AMDAPi SDK can be installed from pip as follows:
```bash
pip install amdapi
```

---------

## **Quick-Start Guide**
<br/>
In order to create a client and use the AMDAPi services, you must first be granted credentials from
<a href="https://www.amdapi.com/" target="_blank">AMDAPi.</a><br>
Once you have these credentials this Quick-Start guide can be followed to quickly understand the main functionality of the SDK.<br>
If further explanation is required the full documentation can be found <a href="#reference-docs">here</a>.
<br/>

------------
<br/>

### **Creating a Client**

```python
from amdapi import Client

amdapi_id = "XXXXXXXXXXXXXXXXXXXXXXXXXX"
amdapi_secret = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

client = Client(amdapi_id, amdapi_secret)

```
or credentials can be loaded into local environment variables

```python
import os
from amdapi import Client
from amdapi.configs import CLIENT_ID_ENV_NAME, CLIENT_SECRET_ENV_NAME

# Client looks for the ID @ AMDAPI-CLIENT-ID 
os.environ[CLIENT_ID_ENV_NAME] = "XXXXXXXXXXXXXXXXXXXXXXXXXX"

# Client looks for the Secret @ AMDAPI-CLIENT-SECRET
os.environ[CLIENT_SECRET_ENV_NAME] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"

client = Client()
```
**Output**:
```python
< amdapi.Client | ClientID: XXXXXXXXXXXXXXXXXXXXXXXXXX | Last Token Refresh: 2022-04-29 08:43:49>
```

---------
### **Analyzing a Call**
<br/>

To send a call to the AMDAPi Backend the following parameters are required.  
**Note**: Currently the audio file must be in a `.wav` format.  
<br/>
#### **Call Params**

| **Name**    	| **Type** 	| **Allowed Values**       	| **Description**                                         	|
|-------------	|----------	|--------------------------	|---------------------------------------------------------	|
| `call_id`     	| `str`      	| NA                       	| ID of Call from your DB                                 	|
| `client_id`   	| `int`      	| NA                       	| ID of Client from your DB                               	|
| `agent_id`    	| `int`      	| NA                       	| ID of Agent from your DB                                	|
| `customer_id` 	| `int`      	| NA                       	| ID of Customer from your DB                             	|
| `summary`     	| `bool`     	| NA                       	| Wheather the call should be summarised during analysis. 	|
| `filename`    	| `str`      	| NA                       	| Filename of the audio file.                             	|
| `origin`      	| `str`      	| `['Inbound','Outbound']` 	| Defines whether the call was Outbound or Inbound.       	|
| `language`    	| `str`      	| `['en','en-in','fr']`    	| Primary language of the audio sent for analysis.        	|
<br/>

#### **Example**
The following code segment demonstrates how you would analyze a call:

```python
filename =  "6c89833033cd57c3cfeb1ad8445821a6714d9bf6cd3613b723ac1cfb"
file_path = f"{filename}.wav"
params = {
        "client_id": 12345,
        "agent_id": 12345,
        "filename": filename,
        "call_id": 12345,
        "customer_id": 12345,
        "origin":"Inbound",
        "language":"en",
        "summary": True
        }

with open(file_path, 'rb') as file:
    call = client.analyze_call(file, **params)
```
  
A `Call` object containing the meta-data provided and the automatically generated uuid will be returned.  
Please allow a few minutes for the analysis of the call to be complete, and retrieve the analyzed call using the call UUID.  
**Output**:
```python
< amdapi.Call | UUID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX | Analyzed: False >
```

---------
<br/>

### **Retrieving A Call**

Retrieving a call via UUID can be achieved as follows:  

```python
call = client.get_call(call.uuid)
```
**Output**:
```python
< amdapi.Call | UUID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX | Analyzed: True >
```
---------
<br/>

### **Searching for Multiple Calls**
The SDK allows for searching for all previously uploaded calls and will return results in a paginated format with max 350 calls per page.
<br/>
<br/>

#### **Search params**
Currently these search parameters are supported, they may be left `None` to get all calls. 
| **Name**    	| **Type**                 	| **Allowed Values**               	| **Description**                	|
|-------------	|--------------------------	|----------------------------------	|--------------------------------	|
| `page_number` 	| `int`                      	| NA                               	| The page number                	|
| `agent_id`    	| `int`                      	| NA                               	| ID of Client from your DB      	|
| `client_id`   	| `int`                      	| NA                               	| ID of Agent from your DB       	|
| `start_date`  	| `str` \| `datetime.datetime` 	| `"DD/MM/YYYY"` - If string is used.	| The start date of your search. 	|
| `end_date`    	| `str` \| `datetime.datetime` 	| `"DD/MM/YYYY"` - If string is used 	| The end date of your search.   	|
<br/>

#### **Example**

```python
search_params = {
    "page_number": 123,
    "agent_id": 123,
    "client_id": 123,
    "start_date": 25/07/2021,
    "end_date": datetime.now(),
    }

search = client.search_calls(**search_params)
```


**Output [No Calls Found]**:
```python
< amdapi.SearchResult | current_page: None | is_last_page: None | n_calls 0 >
```


**Output [Calls Found]**:
```python
< amdapi.SearchResult | current_page: 1 | is_last_page: False | n_calls 350 >
```


#### **Default Search**
If no Search Parameters are provided then all calls will be returned.

```python
search = client.search_calls()
```
**Output**:
```python
< amdapi.SearchResult | current_page: 1 | is_last_page: False | n_calls 350 >
```

----------------------------------------------------------------
<br/>

### **Deleting Calls**

 > ⚠ **WARNING - This action is irreversible**  

You can delete a call and all analysis from the AMDAPi servers with the following: 
```python 
msg = client.delete_call(call.uuid)
```

**Output**:
```python
'Call XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX Deleted Successfully'
```

---------
## **Reference Docs**

Find our full documentation [here](https://amdapi.notion.site/AMDAPi-Python-SDK-d294d978665d4b558d9af87a3e3802c7).