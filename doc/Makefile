# Tweak these to your local configuration. 

EPYDOC=epydoc

# No user-serviceable parts below this line

MODULES=../Kiwi2/Views.py ../Kiwi2/Proxies.py \
		../Kiwi2/__init__.py ../Kiwi2/Delegates.py ../Kiwi2/utils.py \
		../Kiwi2/Models.py ../Kiwi2/Widgets/

STYLE="PRE { border-left: 1px dashed blue;		\
		  border-right: 1px dashed blue;		\
		  border-top: 1px dashed blue;			\
		  border-bottom: 1px dashed blue;		\
		  padding: 1em; margin-right: 2.5em;	\
		  margin-left: 2.5em; }"
NAME=Kiwi2
URL=http://www.async.com.br/projects/Kiwi2/

all: api

api: $(MODULES)
	mkdir -p api
	$(EPYDOC) -c white --no-frames -o api -u $(URL) -n $(NAME) $(MODULES) 
	touch api

apicheck: 
	epydoc --check $(MODULES) 

clean:
	rm -rf api/ howto/ *.log *.aux *.l2h *.dvi *.ps *.bak *~

.PHONY: apicheck clean
