import requests
import json
import csv
import datetime


def getCreds() :
	""" Get creds required for use in the applications
	
	Returns:
		dictionary: credentials needed globally

	"""

	creds = dict() # dictionary to hold everything
	creds['access_token'] = [your-access-token] # access token for use with all api calls
	creds['graph_domain'] = 'https://graph.instagram.com/' # base domain for api calls
	creds['graph_version'] = 'v22.0' # version of the api we are hitting
	creds['endpoint_base'] = creds['graph_domain'] + creds['graph_version'] + '/' # base endpoint with domain and version
	creds['debug'] = 'no' # debug mode for api call
	creds['instagram_account_id'] = [your-account-id] # users instagram account id
	creds['ig_username'] = [your-username] # ig username

	return creds

def makeApiCall( url, endpointParams, debug = 'no' ) :
	""" Request data from endpoint with params
	
	Args:
		url: string of the url endpoint to make request from
		endpointParams: dictionary keyed by the names of the url parameters


	Returns:
		object: data from the endpoint

	"""

	data = requests.get( url, endpointParams ) # make get request

	response = dict() # hold response info
	response['url'] = url # url we are hitting
	response['endpoint_params'] = endpointParams #parameters for the endpoint
	response['endpoint_params_pretty'] = json.dumps( endpointParams, indent = 4 ) # pretty print for cli
	response['json_data'] = json.loads( data.content ) # response data from the api
	response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

	if ( 'yes' == debug ) : # display out response info
		displayApiCallData( response ) # display response

	return response # get and return content

def displayApiCallData( response ) :
	""" Print out to cli response from api call """

	print("\nURL: ") # title
	print(response['url']) # display url hit
	print("\nEndpoint Params: ") # title
	print(response['endpoint_params_pretty']) # display params passed to the endpoint
	print("\nResponse: ") # title
	print(response['json_data_pretty']) # make look pretty for cli

def getUserMedia( params ) :
	""" Get users media
	
	API Endpoint:
		https://graph.instagram.com/{graph-api-version}/{ig-user-id}/media?fields={fields}

	Returns:
		object: data from the endpoint

	"""

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['fields'] = 'id,caption,media_type,comments_count,permalink,like_count,timestamp,username,shares' # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['instagram_account_id'] + '/media' # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call

def getMediaInsights( params ) :
	""" Get insights for a specific media id
	
	API Endpoint:
		https://graph.instagram.com/{graph-api-version}/{ig-media-id}/insights?metric={metric}

	Returns:
		object: data from the endpoint

	"""
	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['metric'] = params['metric'] # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['latest_media_id'] + '/insights' # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call

def getUserPage( params ) :
	""" Get users account info
	
	API Endpoint:
		https://graph.instagram.com/{graph-api-version}/{ig-user-id}/insights?metric={metric}&period={period}

	Returns:
		object: data from the endpoint

	"""
	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['fields'] = 'id,username,name,biography,media_count,followers_count,follows_count' # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['instagram_account_id'] # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call

def getUserInsights( params ) :
	""" Get insights for a users account
	
	API Endpoint:
		https://graph.instagram.com/{graph-api-version}/{ig-user-id}/insights?metric={metric}&period={period}

	Returns:
		object: data from the endpoint

	"""

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['metric'] = 'accounts_engaged,comments,views,profile_views,reach,engaged_audience_demographics,follows_and_unfollows,follower_demographics,likes,replies,total_interactions' # fields to get back
	endpointParams['period'] = 'day' # period
	endpointParams['breakdown'] = 'media_product_type' # breakdown
	endpointParams['access_token'] = params['access_token'] # access token

	url = params['endpoint_base'] + params['instagram_account_id'] + '/insights' # endpoint url

	return makeApiCall( url, endpointParams, params['debug'] ) # make the api call


current_time = datetime.datetime.now()

# Get the content and details of each post
params = getCreds() # get creds
response = getUserMedia( params ) # get users media from the api

with open([your-file-path], 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['post_id', 'permalink', 'timestamp', 'media_type', 'caption'])
    for insight in response['json_data']['data'] : # loop over post insights
        writer.writerow([insight['id'], insight['permalink'], insight['timestamp'], insight['media_type'], insight['caption']])



# Get detailed insights for each post
with open([your-file-path], 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    #writer.writerow(['retrieved_time', 'post_id', 'likes', 'comments', 'shares', 'saved', 'total_interactions', 'reach', 'views', 'profile_activity', 'profile_visits', 'reels_avg_watch_time (ms)', 'reels_total_watch_time (ms)'])
    for insight in response['json_data']['data'] : # loop over post insights
        params['latest_media_id'] = insight['id']
        if 'VIDEO' == insight['media_type'] : # media is a video
            params['metric'] = 'likes,comments,shares,saved,total_interactions,reach,views,ig_reels_avg_watch_time,ig_reels_video_view_total_time'
        else : # media is an image
            params['metric'] = 'likes,comments,shares,saved,total_interactions,reach,views,profile_activity,profile_visits'    
        insights_response = getMediaInsights( params )['json_data']['data']
        
        if 'VIDEO' == insight['media_type'] :
        	writer.writerow([current_time, insights_response[0]['id'].split('/')[0], insights_response[0]['values'][0]['value'], insights_response[1]['values'][0]['value'], insights_response[2]['values'][0]['value'], insights_response[3]['values'][0]['value'], insights_response[4]['values'][0]['value'], insights_response[5]['values'][0]['value'], insights_response[6]['values'][0]['value'], None, None, insights_response[7]['values'][0]['value'], insights_response[8]['values'][0]['value']]) # display info
        else : # media is an image
        	writer.writerow([current_time, insights_response[0]['id'].split('/')[0], insights_response[0]['values'][0]['value'], insights_response[1]['values'][0]['value'], insights_response[2]['values'][0]['value'], insights_response[3]['values'][0]['value'], insights_response[4]['values'][0]['value'], insights_response[5]['values'][0]['value'], insights_response[6]['values'][0]['value'], insights_response[7]['values'][0]['value'], insights_response[8]['values'][0]['value']]) # display info


response = getUserPage( params )

with open([your-file-path], 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    #writer.writerow(['retrieved_time', 'username', 'name', 'biography', 'posts', 'followers', 'follows'])
    writer.writerow([current_time, response['json_data']['username'], response['json_data']['name'], response['json_data']['biography'], response['json_data']['media_count'], response['json_data']['followers_count'], response['json_data']['follows_count']])


response = getUserInsights( params ) # get insights for a user
with open([your-file-path], 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    #writer.writerow(['retrieved_time', 'reach'])
    writer.writerow([current_time, response['json_data']['data'][0]['values'][0]['value']])

