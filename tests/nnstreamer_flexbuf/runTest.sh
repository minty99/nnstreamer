#!/usr/bin/env bash
##
## SPDX-License-Identifier: LGPL-2.1-only
##
## @file runTest.sh
## @author Gichan Jang <gichan2.jang@samsung.com>
## @date Mar 12 2021
## @brief SSAT Test Cases for flexbuffers subplugin of tensor converter and decoder
## @details After decoding the tensor into flexbuffer, convert it to tensor(s) again to check if it matches the original
##
if [[ "$SSATAPILOADED" != "1" ]]; then
    SILENT=0
    INDEPENDENT=1
    search="ssat-api.sh"
    source $search
    printf "${Blue}Independent Mode${NC}"
fi

# This is compatible with SSAT (https://github.com/myungjoo/SSAT)
testInit $1

if [ "$SKIPGEN" == "YES" ]; then
    echo "Test Case Generation Skipped"
    sopath=$2
else
    echo "Test Case Generation Started"
    python ../nnstreamer_converter/generateGoldenTestResult.py 9
    python3 ../nnstreamer_merge/generateTest.py
    sopath=$1
fi
convertBMP2PNG

PATH_TO_PLUGIN="../../build"

if [[ -d $PATH_TO_PLUGIN ]]; then
    ini_path="${PATH_TO_PLUGIN}/ext/nnstreamer/tensor_converter"
    if [[ -d ${ini_path} ]]; then
        check=$(ls ${ini_path} | grep flexbuf.so)
        if [[ ! $check ]]; then
            echo "Cannot find flexbuf shared lib"
            report
            exit
        fi
    else
        echo "Cannot find ${ini_path}"
    fi
else
    echo "No build directory"
    report
    exit
fi

##
## @brief Execute gstreamer pipeline and compare the output of the pipeline
## @param $1 Colorspace
## @param $2 Width
## @param $3 Height
## @param $4 Test Case Number
function do_test() {
    gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} videotestsrc num-buffers=3 pattern=13 ! video/x-raw,format=${1},width=${2},height=${3},framerate=5/1 ! \
    tee name=t ! queue ! multifilesink location=\"raw_${1}_${2}x${3}_%1d.log\"
    t. ! queue ! tensor_converter ! tensor_decoder mode=flexbuf ! other/flexbuf ! tensor_converter ! multifilesink location=\"flexb_${1}_${2}x${3}_%1d.log\" sync=true" ${4} 0 0 $PERFORMANCE

    callCompareTest raw_${1}_${2}x${3}_0.log flexb_${1}_${2}x${3}_0.log "${4}-1" "flexbuf conversion test ${4}-1" 1 0
    callCompareTest raw_${1}_${2}x${3}_1.log flexb_${1}_${2}x${3}_1.log "${4}-2" "flexbuf conversion test ${4}-2" 1 0
    callCompareTest raw_${1}_${2}x${3}_2.log flexb_${1}_${2}x${3}_2.log "${4}-3" "flexbuf conversion test ${4}-3" 1 0
}
# The width and height of video should be multiple of 4
do_test BGRx 320 240 1-1
do_test RGB 320 240 1-2
do_test GRAY8 320 240 1-3

# audio format S16LE, 8k sample rate, samples per buffer 8000
gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} audiotestsrc num-buffers=1 samplesperbuffer=8000 ! audioconvert ! audio/x-raw,format=S16LE,rate=8000 ! \
    tee name=t ! queue ! audioconvert ! tensor_converter frames-per-tensor=8000 ! tensor_decoder mode=flexbuf ! \
        other/flexbuf ! tensor_converter ! filesink location=\"test.audio8k.s16le.log\" sync=true \
    t. ! queue ! filesink location=\"test.audio8k.s16le.origin.log\" sync=true" 2-1 0 0 $PERFORMANCE
callCompareTest test.audio8k.s16le.origin.log test.audio8k.s16le.log 2-2 "Audio8k-s16le Golden Test" 0 0

# audio format U8, 16k sample rate, samples per buffer 8000
gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} audiotestsrc num-buffers=1 samplesperbuffer=8000 ! audioconvert ! audio/x-raw,format=U8,rate=16000 ! \
    tee name=t ! queue ! audioconvert ! tensor_converter frames-per-tensor=8000 ! tensor_decoder mode=flexbuf ! \
        other/flexbuf ! tensor_converter ! filesink location=\"test.audio16k.u8.log\" sync=true \
    t. ! queue ! filesink location=\"test.audio16k.u8.origin.log\" sync=true" 2-3 0 0 $PERFORMANCE
callCompareTest test.audio16k.u8.origin.log test.audio16k.u8.log 2-4 "Audio16k-u8 Golden Test" 0 0

# audio format U16LE, 16k sample rate, 2 channels, samples per buffer 8000
gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} audiotestsrc num-buffers=1 samplesperbuffer=8000 ! audioconvert ! audio/x-raw,format=U16LE,rate=16000,channels=2 ! \
    tee name=t ! queue ! audioconvert ! tensor_converter frames-per-tensor=8000 ! tensor_decoder mode=flexbuf ! \
        other/flexbuf ! tensor_converter ! filesink location=\"test.audio16k2c.u16le.log\" sync=true \
    t. ! queue ! filesink location=\"test.audio16k2c.u16le.origin.log\" sync=true" 2-5 0 0 $PERFORMANCE
callCompareTest test.audio16k2c.u16le.origin.log test.audio16k2c.u16le.log 2-6 "Audio16k2c-u16le Golden Test" 0 0

# Test other/tensors
gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} tensor_mux name=tensors_mux sync-mode=basepad sync-option=1:50000000 ! \
    tensor_decoder mode=flexbuf ! other/flexbuf ! tensor_converter ! multifilesink location=testsynch19_%1d.log \
    tensor_mux name=tensor_mux0  sync-mode=slowest ! queue ! tensors_mux.sink_0 \
    tensor_mux name=tensor_mux1  sync-mode=slowest ! queue ! tensors_mux.sink_1 \
    multifilesrc location=\"testsequence03_%1d.png\" index=0 caps=\"image/png, framerate=(fraction)10/1\" ! pngdec ! tensor_converter ! tensor_mux0.sink_0 \
    multifilesrc location=\"testsequence03_%1d.png\" index=0 caps=\"image/png, framerate=(fraction)20/1\" ! pngdec ! tensor_converter ! tensor_mux0.sink_1 \
    multifilesrc location=\"testsequence03_%1d.png\" index=0 caps=\"image/png, framerate=(fraction)30/1\" ! pngdec ! tensor_converter ! tensor_mux1.sink_0 \
    multifilesrc location=\"testsequence03_%1d.png\" index=0 caps=\"image/png, framerate=(fraction)20/1\" ! pngdec ! tensor_converter ! tensor_mux1.sink_1" 3 0 0 $PERFORMANCE
callCompareTest testsynch19_0.golden testsynch19_0.log 3-1 "Tensor mux Compare 3-1" 1 0
callCompareTest testsynch19_1.golden testsynch19_1.log 3-2 "Tensor mux Compare 3-2" 1 0
callCompareTest testsynch19_2.golden testsynch19_2.log 3-3 "Tensor mux Compare 3-3" 1 0
callCompareTest testsynch19_3.golden testsynch19_3.log 3-4 "Tensor mux Compare 3-4" 1 0
callCompareTest testsynch19_4.golden testsynch19_4.log 3-5 "Tensor mux Compare 3-5" 1 0

# Consecutive converting test
gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} audiotestsrc num-buffers=1 samplesperbuffer=8000 ! audioconvert ! audio/x-raw,format=S16LE,rate=8000 ! \
    tee name=t ! queue ! audioconvert ! tensor_converter frames-per-tensor=8000 ! \
    tensor_decoder mode=flexbuf ! other/flexbuf ! tensor_converter ! \
    tensor_decoder mode=flexbuf ! other/flexbuf ! tensor_converter ! \
    tensor_decoder mode=flexbuf ! other/flexbuf ! tensor_converter ! filesink location=\"test.consecutive.log\" sync=true \
    t. ! queue ! filesink location=\"test.audio8k.s16le.origin.log\" sync=true" 4 0 0 $PERFORMANCE
callCompareTest test.audio8k.s16le.origin.log test.consecutive.log 4-1 "Consecutive converting test" 0 0

# Test flexible tensors (single frame)
gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} videotestsrc num-buffers=3 pattern=13 ! video/x-raw,format=RGB,width=640,height=480,framerate=5/1 ! \
tensor_converter ! other/tensors,format=flexible ! tee name=t ! queue ! multifilesink location=\"flex_raw_5_%1d.log\" \
t. ! queue ! tensor_decoder mode=flexbuf ! other/flexbuf ! tensor_converter ! multifilesink location=\"flex_flxb_5_%1d.log\" sync=true" 5 0 0 $PERFORMANCE
callCompareTest flex_raw_5_0.log flex_flxb_5_0.log "5-0" "Flexbuf flex tensors conversion test 5-0" 1 0
callCompareTest flex_raw_5_1.log flex_flxb_5_1.log "5-1" "Flexbuf flex tensors conversion test 5-1" 1 0
callCompareTest flex_raw_5_2.log flex_flxb_5_2.log "5-2" "Flexbuf flex tensors conversion test 5-2" 1 0


# Test flexible tensors (multi frames, static + flexible = flexible -> flexbuf)
gstTest "--gst-plugin-path=${PATH_TO_PLUGIN} \
    videotestsrc num-buffers=3 pattern=13 ! video/x-raw,format=RGB,width=640,height=480,framerate=5/1 ! tensor_converter ! mux.sink_0 \
    videotestsrc num-buffers=3 pattern=18 ! video/x-raw,format=RGB,width=640,height=480,framerate=5/1 ! tensor_converter ! other/tensors,format=flexible ! mux.sink_1 \
    tensor_mux name=mux ! tee name=t t. ! queue ! multifilesink location=\"flex_mux_raw_6_%1d.log\" sync=true \
    t. ! queue ! tensor_decoder mode=flexbuf ! other/flexbuf ! tensor_converter ! multifilesink location=\"flex_mux_flxb_6_%1d.log\" sync=true" 6 0 0 $PERFORMANCE
callCompareTest flex_mux_raw_6_0.log flex_mux_flxb_6_0.log "6-0" "Flexbuf flex tensors conversion test 6-0" 1 0
callCompareTest flex_mux_raw_6_1.log flex_mux_flxb_6_1.log "6-1" "Flexbuf flex tensors conversion test 6-1" 1 0
callCompareTest flex_mux_raw_6_2.log flex_mux_flxb_6_2.log "6-2" "Flexbuf flex tensors conversion test 6-2" 1 0

rm *.log *.bmp *.png *.golden *.dat

report
