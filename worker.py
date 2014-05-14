from celery import Celery

import os

from wekeypedia.wikipedia_page import WikipediaPage as Page, url2title, url2lang

from wekeypedia.dataset import Dataset


rabbitmq_host = os.environ['RABBITMQ_PORT_5672_TCP_ADDR']
mongodb_host = os.environ['MONGODB_PORT_27017_TCP_ADDR']

BROKER_URL = 'amqp://worker:98b4840644@%s:5672/worker'  % (rabbitmq_host)
RESULTS_URL = 'mongodb://%s:27017//' % (mongodb_host)

print "broker host: %s" % (BROKER_URL)
print "results host: %s" % (RESULTS_URL)

app = Celery(broker=BROKER_URL)

app.conf.update(
#  CELERY_BROKER_URL=BROKER_URL,
  CELERY_RESULT_BACKEND=RESULTS_URL,
  CELERY_ACCEPT_CONTENT = ['application/json'],
  CELERY_TASK_SERIALIZER = "json"
)

@app.task
def dataset_blocks():
  pass

@app.task
def store_revisions(page_url):
  p = Page()

  d = Dataset( "%s:27017" % (mongodb_host) )

  title = url2title(page_url)
  lang = url2lang(page_url)

  p.fetch_from_api_title(title, lang=lang)

  revisions = p.get_all_editors()

  for revision in revisions:
    # ex: en/crimea/revision/999999
    key = "%s/%s/revision/%s" % (lang,title,revision["revid"])

    # fetch the revision from the internet
    value = p.get_revisions(extra_params={ "rvstartid": revision["revid"], "rvlimit" : 1})

    # write in it the database handler
    d.write(key, value)