FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
RUN mkdir /opt && cd /opt && \
    curl -L $OPENCV | tar zx && \
    cd opencv-$OPENCV_VER && \
    mkdir build && cd build && \
    cmake -G Ninja \
          -D CMAKE_BUILD_TYPE=RELEASE \
          -D CMAKE_INSTALL_PREFIX=/usr/local \
          -D WITH_FFMPEG=NO \
          -D WITH_IPP=NO \
          -D PYTHON_EXECUTABLE=/usr/bin/python3 \
          -D WITH_OPENEXR=NO .. && \
    ninja && ninja install && \
    cp -p $(find /usr/local/lib/python3.6/site-packages -name cv2.*.so) \
    /usr/lib/python3.6/site-packages/cv2.so