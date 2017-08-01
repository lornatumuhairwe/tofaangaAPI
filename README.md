# TOFAANGA

[![Codeship Status for lornatumuhairwe/tofaangaAPI](https://app.codeship.com/projects/a14e2a10-58c4-0135-5a0a-5ec3d4c61cb2/status?branch=master)](https://app.codeship.com/projects/236419)
[![Coverage Status](https://coveralls.io/repos/github/lornatumuhairwe/tofaangaAPI/badge.svg?branch=master)](https://coveralls.io/github/lornatumuhairwe/tofaangaAPI?branch=master)
[![Code Climate](https://codeclimate.com/github/lornatumuhairwe/tofaangaAPI/badges/gpa.svg)](https://codeclimate.com/github/lornatumuhairwe/tofaangaAPI)
[![Issue Count](https://codeclimate.com/github/lornatumuhairwe/tofaangaAPI/badges/issue_count.svg)](https://codeclimate.com/github/lornatumuhairwe/tofaangaAPI)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6cec6f639a5048748b9d0e3054645054)](https://www.codacy.com/app/lornatumuhairwe/tofaangaAPI?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=lornatumuhairwe/tofaangaAPI&amp;utm_campaign=Badge_Grade)

The name of this application is based on a Luganda word TOFAANGA' that means DON'T DIE BEFORE ...
It is a simple bucketlist application that helps users to track their goals by allowing a logged in user to create
bucketlists, add items to the different buckets, view the items in the bucketlists and also be able to delete the bucketlists.

### Prerequisites
Check the requirements.txt file

### API routes

| EndPoint | Functionality |
| -------- | ------------- |
| [ POST /auth/login ](#) | Logs a user in |
| [ POST /auth/register ](#) | Register a user |
| [ POST /bucketlists/ ](#) | Create a new bucket list |
| [ GET /bucketlists/ ](#) | List all the created bucket lists |
| [ GET /bucketlists/\<id> ](#) | Get single bucket list |
| [ PUT /bucketlists/\<id> ](#) | Update this bucket list |
| [ DELETE /bucketlists/\<id> ](#) | Delete this single bucket list |
| [ POST /bucketlists/\<id>/items/ ](#) | Create a new item in bucket list |
| [ PUT /bucketlists/\<id>/items/<item_id> ](#) | Update a bucket list item |
| [ DELETE /bucketlists/\<id>/items/<item_id> ](#) | Delete an item in a bucket list |
| [ GET /bucketlists?limit=\<number> ](#) | Gets a number of bucket lists relative to the value passed in number. Maximum records is 100 |
| [ GET /bucketlists?q=\<bucketlist_name> ](#) | Search for bucket list with the same name as that passed in bucketlist_name |
