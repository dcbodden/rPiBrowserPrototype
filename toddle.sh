
TODDLE_CONTENT_BASE=`pwd`
export TODDLE_CONTENT="file:${TODDLE_CONTENT_BASE}/contentroot/content1.html"
#echo CONTENT: $TODDLE_CONTENT
sudo TODDLE_CONTENT="file:${TODDLE_CONTENT_BASE}/contentroot/content1.html" python ./browser.py
