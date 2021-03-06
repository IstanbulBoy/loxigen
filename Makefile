# Copyright 2013, Big Switch Networks, Inc.
#
# LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
# the following special exception:
#
# LOXI Exception
#
# As a special exception to the terms of the EPL, you may distribute libraries
# generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
# that copyright and licensing notices generated by LoxiGen are not altered or removed
# from the LoxiGen Libraries and the notice provided below is (i) included in
# the LoxiGen Libraries, if distributed in source code form and (ii) included in any
# documentation for the LoxiGen Libraries, if distributed in binary form.
#
# Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
#
# You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
# a copy of the EPL at:
#
# http://www.eclipse.org/legal/epl-v10.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# EPL for the specific language governing permissions and limitations
# under the EPL.

# Available targets: all, c, python, clean

# This Makefile is just for convenience. Users that need to pass additional
# options to loxigen.py are encouraged to run it directly.

# Where to put the generated code.
LOXI_OUTPUT_DIR = loxi_output

# Generated files depend on all Loxi code and input files
LOXI_PY_FILES=$(shell find . \( -name loxi_output -prune \
                             -o -name templates -prune \
                             -o -name tests -prune \
                             -o -name '*' \
                           \) -a -name '*.py')
LOXI_TEMPLATE_FILES=$(shell find */templates -type f -a \
                                 \! \( -name '*.cache' -o -name '.*' \))
JAVA_PRE_WRITTEN_FILES=$(shell find java_gen/pre-written -type f)
INPUT_FILES = $(wildcard openflow_input/*)
TEST_DATA = $(shell find test_data -name '*.data')
OPENFLOWJ_OUTPUT_DIR = ${LOXI_OUTPUT_DIR}/openflowj
OPENFLOWJ_ECLIPSE_WORKSPACE = openflowj-loxi

all: c python java wireshark

c: .loxi_ts.c

.loxi_ts.c: ${LOXI_PY_FILES} ${LOXI_TEMPLATE_FILES} ${INPUT_FILES} ${TEST_DATA}
	./loxigen.py --install-dir=${LOXI_OUTPUT_DIR} --lang=c
	touch $@

python: .loxi_ts.python

.loxi_ts.python: ${LOXI_PY_FILES} ${LOXI_TEMPLATE_FILES} ${INPUT_FILES} ${TEST_DATA}
	./loxigen.py --install-dir=${LOXI_OUTPUT_DIR} --lang=python
	touch $@

python-doc: python
	rm -rf ${LOXI_OUTPUT_DIR}/pyloxi-doc
	mkdir -p ${LOXI_OUTPUT_DIR}/pyloxi-doc
	cp -a py_gen/sphinx ${LOXI_OUTPUT_DIR}/pyloxi-doc/input
	PYTHONPATH=${LOXI_OUTPUT_DIR}/pyloxi sphinx-apidoc -o ${LOXI_OUTPUT_DIR}/pyloxi-doc/input ${LOXI_OUTPUT_DIR}/pyloxi
	sphinx-build ${LOXI_OUTPUT_DIR}/pyloxi-doc/input ${LOXI_OUTPUT_DIR}/pyloxi-doc
	rm -rf ${LOXI_OUTPUT_DIR}/pyloxi-doc/input
	@echo "HTML documentation output to ${LOXI_OUTPUT_DIR}/pyloxi-doc"

java: .loxi_ts.java
	@rsync -rt java_gen/pre-written/ ${LOXI_OUTPUT_DIR}/openflowj/
	@if [ -e ${OPENFLOWJ_ECLIPSE_WORKSPACE} ]; then \
		rsync --checksum --delete -rv ${LOXI_OUTPUT_DIR}/openflowj/gen-src/ ${OPENFLOWJ_ECLIPSE_WORKSPACE}/gen-src; \
	fi

.loxi_ts.java: ${LOXI_PY_FILES} ${LOXI_TEMPLATE_FILES} ${INPUT_FILES} ${TEST_DATA} ${JAVA_PRE_WRITTEN_FILES}
	./loxigen.py --install-dir=${LOXI_OUTPUT_DIR} --lang=java
	touch $@

eclipse-workspace:
	mkdir -p ${OPENFLOWJ_ECLIPSE_WORKSPACE}
	ln -sf ../java_gen/pre-written/pom.xml ${OPENFLOWJ_ECLIPSE_WORKSPACE}/pom.xml
	ln -sf ../java_gen/pre-written/LICENSE.txt ${OPENFLOWJ_ECLIPSE_WORKSPACE}/LICENSE.txt
	ln -sf ../java_gen/pre-written/src ${OPENFLOWJ_ECLIPSE_WORKSPACE}
	rsync --checksum --delete -rv ${LOXI_OUTPUT_DIR}/openflowj/gen-src/ ${OPENFLOWJ_ECLIPSE_WORKSPACE}/gen-src
	cd ${OPENFLOWJ_ECLIPSE_WORKSPACE} && mvn eclipse:eclipse
	# Unfortunately, mvn eclipse:eclipse resolves the symlink, which doesn't work with eclipse
	cd ${OPENFLOWJ_ECLIPSE_WORKSPACE} && perl -pi -e 's{<classpathentry kind="src" path="[^"]*/java_gen/pre-written/src/}{<classpathentry kind="src" path="src/}' .classpath

check-java: java
	cd ${OPENFLOWJ_OUTPUT_DIR} && mvn compile test-compile test

package-java: java
	cd ${OPENFLOWJ_OUTPUT_DIR} && mvn package

deploy-java: java
	cd ${OPENFLOWJ_OUTPUT_DIR} && mvn deploy

install-java: java
	cd ${OPENFLOWJ_OUTPUT_DIR} && mvn install

wireshark: .loxi_ts.wireshark

.loxi_ts.wireshark: ${LOXI_PY_FILES} ${LOXI_TEMPLATE_FILES} ${INPUT_FILES}
	./loxigen.py --install-dir=${LOXI_OUTPUT_DIR} --lang=wireshark
	touch $@

clean:
	rm -rf loxi_output # only delete generated files in the default directory
	rm -f loxigen.log loxigen-test.log .loxi_ts.*

debug:
	@echo "LOXI_OUTPUT_DIR=\"${LOXI_OUTPUT_DIR}\""
	@echo
	@echo "LOXI_PY_FILES=\"${LOXI_PY_FILES}\""
	@echo
	@echo "LOXI_TEMPLATE_FILES=\"${LOXI_TEMPLATE_FILES}\""
	@echo
	@echo "INPUT_FILES=\"${INPUT_FILES}\""

check-all: check check-c check-py check-java

check:
	nosetests

check-py: python
	PYTHONPATH=${LOXI_OUTPUT_DIR}/pyloxi:. python py_gen/tests/generic_util.py
	PYTHONPATH=${LOXI_OUTPUT_DIR}/pyloxi:. python py_gen/tests/of10.py
	PYTHONPATH=${LOXI_OUTPUT_DIR}/pyloxi:. python py_gen/tests/of11.py
	PYTHONPATH=${LOXI_OUTPUT_DIR}/pyloxi:. python py_gen/tests/of12.py
	PYTHONPATH=${LOXI_OUTPUT_DIR}/pyloxi:. python py_gen/tests/of13.py
	PYTHONPATH=${LOXI_OUTPUT_DIR}/pyloxi:. python py_gen/tests/of14.py

check-c: c
	make -j4 -C ${LOXI_OUTPUT_DIR}/locitest
	${LOXI_OUTPUT_DIR}/locitest/locitest

pylint:
	pylint -E ${LOXI_PY_FILES}

ctags:
	ctags ${LOXI_PY_FILES} ${LOXI_TEMPLATE_FILES} ${INPUT_FILES} ${TEST_DATA}

coverage:
	find -name '*,cover' -exec rm {} \;
	coverage erase
	coverage run -a ./loxigen.py --lang=c
	coverage run -a ./loxigen.py --lang=python
	coverage run -a ./loxigen.py --lang=java
	coverage run -a ./loxigen.py --lang=wireshark
	coverage annotate -i --omit tenjin.py,pyparsing.py

.PHONY: all clean debug check pylint c python coverage
