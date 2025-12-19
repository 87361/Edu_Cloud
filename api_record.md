//获取本学期课程列表
  GET /ykt-site/site/list/student/current
  接口ID：392211697
  接口地址：https://app.apifox.com/link/project/7569333/apis/api-392211697

//请求代码（两种）
import http.client

conn = http.client.HTTPSConnection("apiucloud.bupt.edu.cn")
payload = ''
headers = {}
conn.request("GET", "/ykt-site/site/list/student/current?size=999999&current=1&userId=1234567890123456789&siteRoleCode=2", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

import requests

url = "https://apiucloud.bupt.edu.cn/ykt-site/site/list/student/current?size=999999&current=1&userId=1234567890123456789&siteRoleCode=2"

payload={}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

//返回响应示例
{

    "code": 200,

    "success": true,

    "data": {

        "records": [

            {

                "id": "1957690181209296898",

                "siteName": "Python程序设计",

                "termId": "1693148401899671553",

                "departmentId": "1401097964818010113",

                "baseCourseId": "1432578672904114179",

                "domainId": "1325774332638531585",

                "isPublic": 1,

                "picUrl": "https://fileucloud.bupt.edu.cn/bupt/upload/20250922/d6d33eda1ff7cfed69158eb89b0729ce.jpeg",

                "createTime": "2025-08-19T14:24:39",

                "updateTime": "2025-09-22T08:27:22",

                "isDelete": 0,

                "certificationType": "",

                "briefIntroduction": "<p> 见大纲 </p>",

                "cloneCode": "22mf4w",

                "courseType": "专业课",

                "kcsx": "必修",

                "kclb": "理论课（不含实践）",

                "isBenchmark": 0,

                "isApproval": 0,

                "isSync": 1,

                "grade": "",

                "specialty": "",

                "department": "计算机学院（国家示范性软件学院）",

                "courseCode": "3132133010",

                "departmentName": "计算机学院（国家示范性软件学院）",

                "domainName": "本科",

                "teacherId": "1401098440073756964",

                "teachers": [

                    {

                        "id": "1401098440073756964",

                        "createTime": "2021-06-05 16:47:54",

                        "status": -1,

                        "tenantId": "000000",

                        "code": "",

                        "account": "2010814015",

                        "name": "谢坤",

                        "realName": "谢坤",

                        "avatar": "https://fileucloud.bupt.edu.cn/ucloud/other/429a477bcc4b7f03e05a67a8bb85fd3f.",

                        "email": "",

                        "phone": "",

                        "birthday": "",

                        "sex": 1,

                        "roleId": "",

                        "deptId": "1401097964818010113",

                        "postId": "",

                        "professional": "讲师（高校）",

                        "joinTime": "2021-01-01",

                        "qq": "",

                        "deptName": "计算机学院（国家示范性软件学院）",

                        "major": "",

                        "tenantName": "",

                        "roleName": "",

                        "postName": "",

                        "sexName": "男"

                    }

                ],

                "primaryTeachers": "",

                "termName": "2025秋季",

                "deptCode": "313",

                "studentNo": 185,

                "primaryTeacherIdList": [],

                "isStickTop": false,

                "isExcellent": false

            }

        ],

        "total": 19,

        "size": 1000,

        "current": 1,

        "orders": [],

        "optimizeCountSql": true,

        "hitCount": false,

        "searchCount": true,

        "pages": 1

    },

    "msg": "操作成功"

}

//获取课程主页讲义
  POST /ykt-site/site-resource/tree/student
  接口ID：392223632
  接口地址：https://app.apifox.com/link/project/7569333/apis/api-392223632

//请求代码（两种）
import http.client

conn = http.client.HTTPSConnection("apiucloud.bupt.edu.cn")
payload = ''
headers = {}
conn.request("POST", "/ykt-site/site-resource/tree/student?siteId=1957690181209296898&userId=1234567890123456789", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))

import requests

url = "https://apiucloud.bupt.edu.cn/ykt-site/site-resource/tree/student?siteId=1957690181209296898&userId=1234567890123456789"

payload={}
headers = {}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)

//示例返回代码
{

  "code": 200,

  "success": true,

  "data": [

    {

      "id": "1963770917409529859",

      "siteId": "1957690181209296898",

      "resourceName": "第01章 Python概述",

      "resourceType": 1,

      "hasFatherNode": 0,

      "hasChildNode": 0,

      "resourceVisible": 1,

      "recommendLearnTime": -1,

      "resourceOrder": 22,

      "fatherNodeId": 0,

      "level": 0,

      "teachingDuration": -1,

      "isDelete": 0,

      "createTime": "2025-09-05T09:07:26",

      "updateTime": "2025-09-05T09:07:26",

      "children": [],

      "attachmentVOs": [

        {

          "id": "1970471216056360962",

          "siteResourceId": "1963770917409529859",

          "siteResourceSetId": "1970471216043778050",

          "attachmentInfoId": "1970316630850744321",

          "accessLimit": 1,

          "isDelete": 0,

          "sort": 1,

          "type": 1,

          "createTime": "2025-09-23 20:52:02",

          "updateTime": "2025-09-23 20:52:02",

          "resource": {

            "id": "1970316630850744321",

            "parentId": "1858337723491057665",

            "author": "1401098440073756964",

            "name": "第01章-Python概述.pptx",

            "fileId": -1,

            "fileSize": 3423092,

            "fileSizeUnit": "3.26MB",

            "ext": "pptx",

            "storageId": "922328088d08c9d61dda32dc008e80d1",

            "link": "",

            "previewStorageId": "",

            "type": 1,

            "mimeType": "application/vnd.openxmlformats-officedocument.presentationml.presentation",

            "description": "",

            "sourceId": "",

            "sourcePic": "",

            "sourceDuration": -1,

            "sourceUrl": "",

            "sourceStatus": -1,

            "isMedia": -1,

            "isShare": 0,

            "isDeleted": 0,

            "isRecycle": 0,

            "classify": 1,

            "bizType": 1,

            "recordFlag": 0,

            "createTime": "2025-09-23 10:37:46",

            "updateTime": "2025-09-23 10:37:46",

            "resourceIdUrl": {},

            "url": "https://fileucloud.bupt.edu.cn/ucloud/document/922328088d08c9d61dda32dc008e80d1.pptx"

          },

          "siteResourceLink": {}

        }

      ]

    },

    {

      "id": "1963770917438889990",

      "siteId": "1957690181209296898",

      "resourceName": "综合项目实践",

      "resourceType": 1,

      "hasFatherNode": 0,

      "hasChildNode": 0,

      "resourceVisible": 1,

      "recommendLearnTime": -1,

      "resourceOrder": 41,

      "fatherNodeId": 0,

      "level": 0,

      "teachingDuration": -1,

      "isDelete": 0,

      "createTime": "2025-09-05T09:07:26",

      "updateTime": "2025-09-05T09:07:26",

      "children": [],

      "attachmentVOs": [

        {

          "id": "1970472603782950914",

          "siteResourceId": "1963770917438889990",

          "siteResourceSetId": "1970472603774562305",

          "attachmentInfoId": "1970439954527326209",

          "accessLimit": 1,

          "isDelete": 0,

          "sort": 1,

          "type": 1,

          "createTime": "2025-09-23 20:57:33",

          "updateTime": "2025-09-23 20:57:33",

          "resource": {

            "id": "1970439954527326209",

            "parentId": "1527435729014521857",

            "author": "1401098440073756964",

            "name": "《Python程序设计》课程实践指导书.pdf",

            "fileId": -1,

            "fileSize": 159152,

            "fileSizeUnit": "155.42KB",

            "ext": "pdf",

            "storageId": "8f85017bc5ddb923d820cf1a1295bb1f",

            "link": "",

            "previewStorageId": "",

            "type": 1,

            "mimeType": "application/pdf",

            "description": "",

            "sourceId": "",

            "sourcePic": "",

            "sourceDuration": -1,

            "sourceUrl": "",

            "sourceStatus": -1,

            "isMedia": -1,

            "isShare": 0,

            "isDeleted": 0,

            "isRecycle": 0,

            "classify": 1,

            "bizType": 1,

            "recordFlag": 0,

            "createTime": "2025-09-23 18:47:49",

            "updateTime": "2025-09-23 18:47:49",

            "resourceIdUrl": {},

            "url": "https://fileucloud.bupt.edu.cn/ucloud/document/8f85017bc5ddb923d820cf1a1295bb1f.pdf"

          },

          "siteResourceLink": {}

        },

        {

          "id": "1970472603787145217",

          "siteResourceId": "1963770917438889990",

          "siteResourceSetId": "1970472603774562305",

          "attachmentInfoId": "1970439954467287041",

          "accessLimit": 1,

          "isDelete": 0,

          "sort": 2,

          "type": 1,

          "createTime": "2025-09-23 20:57:33",

          "updateTime": "2025-09-23 20:57:33",

          "resource": {

            "id": "1970439954467287041",

            "parentId": "1527435729014521857",

            "author": "1401098440073756964",

            "name": "小组实验报告模板.docx",

            "fileId": -1,

            "fileSize": 19189,

            "fileSizeUnit": "18.74KB",

            "ext": "docx",

            "storageId": "3103f797c8c3cac5db3c12eea366708e",

            "link": "",

            "previewStorageId": "",

            "type": 1,

            "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

            "description": "",

            "sourceId": "",

            "sourcePic": "",

            "sourceDuration": -1,

            "sourceUrl": "",

            "sourceStatus": -1,

            "isMedia": -1,

            "isShare": 0,

            "isDeleted": 0,

            "isRecycle": 0,

            "classify": 1,

            "bizType": 1,

            "recordFlag": 0,

            "createTime": "2025-09-23 18:47:49",

            "updateTime": "2025-09-23 18:47:49",

            "resourceIdUrl": {},

            "url": "https://fileucloud.bupt.edu.cn/ucloud/document/3103f797c8c3cac5db3c12eea366708e.docx"

          },

          "siteResourceLink": {}

        }

      ]

    }

  ],

  "msg": "操作成功"

}
