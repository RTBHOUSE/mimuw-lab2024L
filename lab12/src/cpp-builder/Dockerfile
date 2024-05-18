FROM gcc:11

ENV TASK_ID "<to_fill>"
ENV CODE "<to_fill>"

COPY score.sh /userdata/
COPY examples /userdata/examples

WORKDIR /userdata

ENTRYPOINT bash score.sh
