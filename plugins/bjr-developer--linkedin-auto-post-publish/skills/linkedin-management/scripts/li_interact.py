import requests
import json
import os
import time

class LinkedInBot:
    def __init__(self, cookies_file="linkedin_cookies.json"):
        self.cookies_file = cookies_file
        self.session = requests.Session()
        self.csrf_token = ""
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            "accept": "application/vnd.linkedin.normalized+json+2.1",
            "x-li-lang": "en_US",
            "x-restli-protocol-version": "2.0.0",
        }
        self.load_cookies()

    def load_cookies(self):
        if not os.path.exists(self.cookies_file):
            print(f"Error: {self.cookies_file} not found. Please run capture_linkedin_session.py first.")
            return

        with open(self.cookies_file, "r") as f:
            cookies_list = json.load(f)
        
        cookie_dict = {}
        for cookie in cookies_list:
            cookie_dict[cookie['name']] = cookie['value']
            if cookie['name'] == 'JSESSIONID':
                # LinkedIn uses JSESSIONID as CSRF token (usually matches ajax:...)
                # It needs to be stripped of quotes if present
                val = cookie['value'].strip('"')
                self.csrf_token = val
        
        self.session.cookies.update(cookie_dict)
        self.base_headers["csrf-token"] = self.csrf_token
        print(f"Loaded {len(cookie_dict)} cookies. CSRF Token: {self.csrf_token}")

    def create_post(self, text, media_urn=None):
        url = "https://www.linkedin.com/voyager/api/graphql?action=execute&queryId=voyagerContentcreationDashShares.279996efa5064c01775d5aff003d9377"
        
        post_data = {
            "allowedCommentersScope": "ALL",
            "intendedShareLifeCycleState": "PUBLISHED",
            "origin": "FEED",
            "visibilityDataUnion": { "visibilityType": "ANYONE" },
            "commentary": { "text": text, "attributesV2": [] }
        }

        if media_urn:
            post_data["media"] = {
                "category": "IMAGE",
                "mediaUrn": media_urn,
                "tapTargets": [],
                "altText": ""
            }

        payload = {
            "variables": { "post": post_data },
            "queryId": "voyagerContentcreationDashShares.279996efa5064c01775d5aff003d9377",
            "includeWebMetadata": True
        }

        response = self.session.post(url, headers=self.base_headers, json=payload)
        return response.json()

    def edit_post(self, share_urn, activity_id, text):
        """
        share_urn example: urn:li:share:12345
        activity_id example: 12345
        """
        url = "https://www.linkedin.com/voyager/api/graphql?action=execute&queryId=voyagerContentcreationDashShares.d574029ec0bf1cccf71adf61f3dcd498"
        
        payload = {
            "variables": {
                "entity": {
                    "entity": {
                        "commentary": { "text": text, "attributesV2": [] }
                    },
                    "resourceKey": share_urn
                },
                "updateUrn": f"urn:li:fsd_update:(urn:li:activity:{activity_id},MAIN_FEED,EMPTY,DEFAULT,false)"
            },
            "queryId": "voyagerContentcreationDashShares.d574029ec0bf1cccf71adf61f3dcd498",
            "includeWebMetadata": True
        }

        response = self.session.post(url, headers=self.base_headers, json=payload)
        return response.json()

    def delete_post(self, activity_id):
        # Using the exact endpoint captured in the network log
        url = "https://www.linkedin.com/flagship-web/rsc-action/actions/server-request?sduiid=com.linkedin.sdui.update.deletePost"
        
        # Replicating the exact headers required for SDUI actions
        headers = self.base_headers.copy()
        headers.update({
            "Content-Type": "application/json",
            "x-li-anchor-page-key": "d_flagship3_feed",
            "x-li-page-instance": "urn:li:page:d_flagship3_feed;pE8XMk89S0qpSv5uXR9HDA==",
            "x-li-rsc-stream": "true"
        })
        
        payload = {
            "requestId": "com.linkedin.sdui.update.deletePost",
            "serverRequest": {
                "$type": "proto.sdui.actions.core.ServerRequest",
                "requestId": "com.linkedin.sdui.update.deletePost",
                "requestedArguments": {
                    "$type": "proto.sdui.actions.requests.RequestedArguments",
                    "payload": {
                        "updateKeyContainer": {
                            "feedType": 72,
                            "items": [{
                                "feedUpdateUrn": {
                                    "updateUrnActivityUrn": {
                                        "__typename": "proto_com_linkedin_common_ActivityUrn",
                                        "activityUrn": { "activityId": activity_id }
                                    }
                                },
                                "trackingId": "YGOE41KkSISURO5ef788Xg==" # Using a dummy tracking ID if needed
                            }],
                            "aggregationType": 0,
                            "isVideoCarousel": False
                        },
                        "shareLifeCycleState": "ShareLifeCycleState_PUBLISHED",
                        "isUpdateInCarousel": False
                    },
                    "requestedStateKeys": [],
                    "requestMetadata": {
                        "$type": "proto.sdui.common.RequestMetadata"
                    }
                },
                "onClientRequestFailureAction": {
                    "actions": []
                },
                "isStreaming": False,
                "rumPageKey": "",
                "isApfcEnabled": False
            },
            "states": [],
            "requestedArguments": {
                "$type": "proto.sdui.actions.requests.RequestedArguments",
                "payload": {
                    "updateKeyContainer": {
                        "feedType": 72,
                        "items": [{
                            "feedUpdateUrn": {
                                "updateUrnActivityUrn": {
                                    "__typename": "proto_com_linkedin_common_ActivityUrn",
                                    "activityUrn": { "activityId": activity_id }
                                }
                            }
                        }]
                    }
                }
            },
            "screenId": "com.linkedin.sdui.flagshipnav.feed.ControlMenuOptionConfirmationDialog"
        }

        response = self.session.post(url, headers=headers, json=payload)
        return response.status_code

    def _get_sdui_headers(self):
        """Returns headers required for SDUI actions."""
        headers = self.base_headers.copy()
        headers.update({
            "Content-Type": "application/json",
            "x-li-anchor-page-key": "d_flagship3_feed",
            # This instance ID is captured but usually stays valid for a session duration.
            # You must update this with a fresh value from the browser if SDUI actions fail.
            "x-li-page-instance": "urn:li:page:d_flagship3_feed:YOUR_INSTANCE_ID",
            "x-li-rsc-stream": "true"
        })
        return headers

    def react_to_post(self, activity_id, reaction_type="ReactionType_LIKE"):
        """
        reaction_type options: ReactionType_LIKE, ReactionType_EMPATHY, ReactionType_APPRECIATE, ReactionType_ENTERTAINING, ReactionType_INTERESTING
        """
        url = "https://www.linkedin.com/flagship-web/rsc-action/actions/server-request?sduiid=com.linkedin.sdui.reactions.create"
        
        payload = {
            "requestId": "com.linkedin.sdui.reactions.create",
            "serverRequest": {
                "requestedArguments": {
                    "payload": {
                        "threadUrn": {
                            "threadUrnActivityThreadUrn": { 
                                "__typename": "proto_com_linkedin_common_ActivityUrn",
                                "activityUrn": { "activityId": activity_id } 
                            }
                        },
                        "reactionType": reaction_type,
                        "reactionSource": "Update"
                    }
                }
            }
        }

        response = self.session.post(url, headers=self._get_sdui_headers(), json=payload)
        return response.status_code

    def create_comment(self, activity_id, text):
        url = "https://www.linkedin.com/flagship-web/rsc-action/actions/server-request?sduiid=com.linkedin.sdui.comments.createComment"
        
        # Note: In a real scenario, these keys are dynamic and found in the feed HTML/API.
        # We use a placeholder that matches the expected prefix.
        state_key = f"commentBoxText-urn:li:activity:{activity_id}"
        
        payload = {
            "requestId": "com.linkedin.sdui.comments.createComment",
            "serverRequest": {
                "requestedArguments": {
                    "payload": {
                        "collection": {
                            "updateKey": {
                                "feedType": 72,
                                "items": [{
                                    "feedUpdateUrn": {
                                        "updateUrnActivityUrn": {
                                            "__typename": "proto_com_linkedin_common_ActivityUrn",
                                            "activityUrn": { "activityId": activity_id }
                                        }
                                    }
                                }]
                            }
                        },
                        "threadUrn": {
                            "threadUrnActivityThreadUrn": {
                                "__typename": "proto_com_linkedin_common_ActivityUrn",
                                "activityUrn": { "activityId": activity_id }
                            }
                        },
                         "commentFieldBinding": {
                            "key": state_key,
                            "namespace": "MemoryNamespace"
                        },
                        "richCommentFieldBinding": {
                            "key": f"rich-{state_key}",
                            "namespace": "MemoryNamespace"
                        }
                    }
                }
            },
            "states": [
                {
                    "key": state_key,
                    "namespace": "MemoryNamespace",
                    "value": text,
                    "originalProtoCase": "stringValue"
                }
            ]
        }

        response = self.session.post(url, headers=self._get_sdui_headers(), json=payload)
        return response.status_code

    def upload_image(self, image_path):
        # 1. Initialize upload
        init_url = "https://www.linkedin.com/voyager/api/voyagerVideoDashMediaUploadMetadata?action=upload"
        filename = os.path.basename(image_path)
        filesize = os.path.getsize(image_path)
        
        payload = {
            "mediaUploadType": "IMAGE_SHARING",
            "fileSize": filesize,
            "filename": filename
        }
        
        res = self.session.post(init_url, headers=self.base_headers, json=payload)
        data = res.json()
        
        upload_url = data['value']['uploadUrl']
        media_urn = data['value']['mediaUrn']
        
        # 2. Upload binary data
        with open(image_path, "rb") as f:
            headers = {
                "csrf-token": self.csrf_token,
                "Content-Type": "image/jpeg"
            }
            # Note: The upload URL is sometimes a different domain (static.linkedin.com)
            # Use a fresh PUT request
            put_res = requests.put(upload_url, data=f, headers=headers)
            
        if put_res.status_code == 201 or put_res.status_code == 200:
            print(f"Image uploaded successfully: {media_urn}")
            return media_urn
        else:
            print(f"Failed to upload image: {put_res.status_code}")
            return None

if __name__ == "__main__":
    # Example usage:
    bot = LinkedInBot()
    # bot.create_post("Hello from my automated bot!")
    # bot.react_to_post("7438440404884279296")
    # bot.create_comment("7438440404884279296", "Nice testing!")
