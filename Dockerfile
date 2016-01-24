FROM prologic/python-runtime:onbuild

RUN make

ENTRYPOINT ["./bin/js"]
