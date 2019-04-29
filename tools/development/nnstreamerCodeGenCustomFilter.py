#!/usr/bin/env python

##
# NNStreamer Custom Filter Code Generator
# Copyright (c) 2019 Samsung Electronics
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.

##
# @file   nnstreamerCodeGenCustomFilter.py
# @brief  A code generator for nnstreamer custom filters.
# @author MyungJoo Ham <myungjoo.ham@samsung.com>
# @date   04 Mar 2019
# @bug    No known bugs

from datetime import date
import sys
import string
import re

def getinput(text):
  if sys.version_info[0] < 3:
    return raw_input(text).strip()
  return input(text).strip()

##
# Common variables for codegen strings
# {name}
# {fname}
# {sname}
# {today}

# The code fragments for codegen
common_head = """/**
* NNStreamer Custom Filter, {name}, created by codegen
* Copyright (C) 2019 Samsung Electronics
*
* LICENSE: LGPL-2.1
*
* @file     nnstreamer_customfilter_{fname}.c
* @date     {today}
* @brief    NNStreamer custom filter generated by codegen, {name}
* @author   MyungJoo Ham <myungjoo.ham@samsung.com>
* @bug      No known bugs
*/

#include <stdlib.h>
#include <assert.h>
#include <tensor_filter_custom.h>
#include <nnstreamer_plugin_api.h>

/**
 * @brief Private Data Structure.
 * @todo Add your own data structure required for the custom filter
 */
typedef struct _{sname}_data
{{
  uint32_t id; /***< Example. Replace with yours */
}} _{sname}_data;

/**
 * @brief Init func called before all other functions.
 * Use this function to initialize data and prepare operations
 * or open/check related resource files
 * @todo Add your own init procedures and _{sname}_data init.
 * @param[in] prop The tensor filter properties (refer to tensor_typedef.h)
 */
static void *
cg_init (const GstTensorFilterProperties * prop)
{{
  _{sname}_data * data;

  data = (_{sname}_data *) malloc (sizeof (_{sname}_data));
  assert (data);

  data->id = 0;
  return data;
}}

/**
 * @brief Exit func called after all other functions.
 * Use this function to deallocate and close resources
 * @todo Add your own exit procedures and _{sname}_data exit.
 * @param[in/out] _data The private data for this custom filter.
 * @param[in] prop The tensor filter properties (refer to tensor_typedef.h)
 */
static void
cg_exit (void * _data, const GstTensorFilterProperties * prop)
{{
  _{sname}_data *data = _data;
  assert (data);
  if (data)
    free (data);
}}
"""

##
# @brief Fixed mode is applicable if input and output dimensions are fixed to single instances.
dim_fixed = """
/**
 * @brief Tell nnstreamer the fixed dimension/type of input tensors
 *
 * @warning Do not fix any internal values based on this function call.
 *          NNStreamer may call this function multiple times before fixing input/output dimensions
 *
 * @param[in/out] _data The private data for this custom filter. As noted, I recommend not to update this based on this function call unless you are aware of the pad-cap negotiation phases of GstBaseFilter class.
 * @param[in] prop The tensor filter properties (refer to tensor_typedef.h)
 * @param[out] in_info The input tensors metadata (number, type, and dimensions)
 * @return 0 if success. Non-zero if failed
 */
static int
cg_getInputDim (void * _data, const GstTensorFilterProperties * prop,
                GstTensorsInfo * in_info)
{{
  _{sname}_data *data = _data;
  /** @todo Apply the metadata of your input tensors */
  int i;

  assert (data);
  in_info->num_tensors = 1; /** @todo MODIFY THIS! */
  in_info->info[0].name = NULL; /** Optional, default is null. Set new memory for tensor name string. */
  in_info->info[0].type = _NNS_UINT8; /** @todo MODIFY THIS! */
  in_info->info[0].dimension[0] = 3; /** @todo MODIFY THIS! */
  in_info->info[0].dimension[1] = 224; /** @todo MODIFY THIS! */
  in_info->info[0].dimension[2] = 224; /** @todo MODIFY THIS! */

  for (i = 3; i < NNS_TENSOR_RANK_LIMIT; i++)
    in_info->info[0].dimension[i] = 1; /** Fill 1 to uninitialized dimension values */

  return 0;
}}

/**
 * @brief Tell nnstreamer the fixed dimension/type of output tensors
 *
 * @warning Do not fix any internal values based on this function call.
 *          NNStreamer may call this function multiple times before fixing input/output dimensions
 *
 * @param[in/out] _data The private data for this custom filter. As noted, I recommend not to update this based on this function call unless you are aware of the pad-cap negotiation phases of GstBaseFilter class.
 * @param[in] prop The tensor filter properties (refer to tensor_typedef.h)
 * @param[out] out_info The output tensors metadata (number, type, and dimensions)
 * @return 0 if success. Non-zero if failed
 */
static int
cg_getOutputDim (void * _data, const GstTensorFilterProperties * prop,
                GstTensorsInfo * out_info)
{{
  _{sname}_data *data = _data;
  /** @todo Apply the metadata of your output tensors */
  int i;

  assert (data);
  out_info->num_tensors = 1; /** @todo MODIFY THIS! */
  out_info->info[0].name = NULL; /** Optional, default is null. Set new memory for tensor name string. */
  out_info->info[0].type = _NNS_UINT8; /** @todo MODIFY THIS! */
  out_info->info[0].dimension[0] = 3; /** @todo MODIFY THIS! */
  out_info->info[0].dimension[1] = 224; /** @todo MODIFY THIS! */
  out_info->info[0].dimension[2] = 224; /** @todo MODIFY THIS! */

  for (i = 3; i < NNS_TENSOR_RANK_LIMIT; i++)
    out_info->info[0].dimension[i] = 1; /** Fill 1 to uninitialized dimension values */

  return 0;
}}

#define cg_setInputDim  (NULL)
"""

##
# @brief Variable mode is applicable if output dimension can be determined by the given input dimension.
dim_variable = """
/**
 * @brief With the given input dimension, return corresponding output dimension.
 *
 * @warning With nnstreamer 0.1.x, we cannot express desired ranges of input dimensions.
 *          Thus, the implementor needs to return error (return non-zero value) if the given
 *          input dimension is not tolerable.
 *
 * @warning Do not fix any internal values based on this function call.
 *          NNStreamer may call this function multiple times before fixing input/output dimensions
 *
 * @param[in/out] _data The private data for this custom filter. As noted, I recommend not to update this based on this function call unless you are aware of the pad-cap negotiation phases of GstBaseFilter class.
 * @param[in] prop The tensor filter properties (refer to tensor_typedef.h)
 * @param[in] in_info The given input tensors (number, type, and dimensions)
 * @param[out] out_info The corresponding output tensors (number, type, and dimensions). Allocated by invoker.
 * @return 0 if success. Non-zero if failed
 */
static int
cg_setInputDim (void * _data, const GstTensorFilterProperties *prop,
                const GstTensorsInfo * in_info, GstTensorsInfo * out_info)
{{
  _{sname}_data *data = _data;
  int i, j;

  assert (data);
  assert (in_info);
  assert (out_info);

  out_info->num_tensors = in_info->num_tensors; /** @todo Configure the number of tensors in a output frame */

  /** @todo Configure the name/type/dimension of tensors in a output frame. */
  for (i = 0; i < out_info->num_tensors; i++) {{
    out_info->info[i].name = NULL; /** Optional, default is null. Set new memory for tensor name string. */
    out_info->info[i].type = in_info->info[i].type;

    for (j = 0; j < NNS_TENSOR_RANK_LIMIT; j++)
      out_info->info[i].dimension[j] = in_info->info[i].dimension[j];
  }}

  return 0;
}}

#define cg_getInputDim  (NULL)
#define cg_getOutputDim (NULL)
"""

##
# @brief Use allocate mode if you want to allocates output memory blocks internally.
invoke_allocate = """

/**
 * @brief Allocate output buffer, process the input, write inference results at the output buffer
 *
 * @param[in/out] _data The private data for this custom filter.
 * @param[in] prop The tensor filter properties (refer to tensor_typedef.h)
 * @param[in] input The input tensors
 * @param[out] output The output tensors.
 * @return 0 if success. Non-zero if failed
 *
 * @note The intput / output dimensions, required for interpreting input/output
 *       pointers, are stored in prop.
 */
static int
cg_allocate_invoke (void * _data, const GstTensorFilterProperties * prop,
                    const GstTensorMemory * input, GstTensorMemory * output)
{{
  int i;

  /** If you want to look at input dimension/type, refer to prop->input_meta */
  const GstTensorsInfo * in_info __attribute__ ((unused)) = &prop->input_meta;
  /** If you want to look at output dimension/type, refer to prop->output_meta */
  const GstTensorsInfo * out_info = &prop->output_meta;

  /** Allocate output buffer */
  for (i = 0; i < out_info->num_tensors; i++)
    output[i].data = malloc (gst_tensor_info_get_size (&out_info->info[i]));

  /** @todo Add your inference code/calls. Fill in the output buffer */
  for (i = 0; i < out_info->num_tensors; i++) {{
    int s, size = gst_tensor_info_get_size (&out_info->info[i]);
    uint8_t *ptr = output[i].data;
    for (s = 0; s < size; s++)
      ptr[s] = (uint8_t) s;
  }}

  return 0;
}}

/**
 * @brief This is called when the pointer allocated by cg_allocate_invoke is to be destroyed.
 * @param[in] data The pointer to be destroyed
 */
static void
cg_destroy_notify (void * data)
{{
  assert (data);
  if (data)
    free (data);
}}

#define cg_invoke (NULL)
"""

##
# @brief Use no-allocate mode if you want to fill in pre-allocated output buffers.
invoke_no_allocate = """

/**
 * @brief Invoke inference. Fill in pre-allocated output buffer.
 * @param[in/out] _data The private data for this custom filter.
 * @param[in] prop The tensor filter properties (refer to tensor_typedef.h)
 * @param[in] input The input tensors
 * @param[out] output The output tensors.
 * @return 0 if success. Non-zero if failed
 */
static int
cg_invoke (void * _data, const GstTensorFilterProperties *prop,
           const GstTensorMemory * input, GstTensorMemory * output)
{{
  int i;

  /** If you want to look at input dimension/type, refer to prop->input_meta */
  const GstTensorsInfo * in_info __attribute__ ((unused)) = &prop->input_meta;
  /** If you want to look at output dimension/type, refer to prop->output_meta */
  const GstTensorsInfo * out_info __attribute__ ((unused)) = &prop->output_meta;

  /** @note Caller will allocate output buffer accornding to out_info. */

  /** @todo Add your inference code/calls. Fill in the output buffer */
  for (i = 0; i < out_info->num_tensors; i++) {{
    int s, size = gst_tensor_info_get_size (&out_info->info[i]);
    uint8_t *ptr = output[i].data;
    for (s = 0; s < size; s++)
      ptr[s] = (uint8_t) s;
  }}

  return 0;
}}

#define cg_allocate_invoke (NULL)
#define cg_destroy_notify (NULL)
"""

##
# @brief Common part finishing up the code.
#
# @todo With progress of #1182, this may need to be updated.
common_tail = """

/**
 * @brief The "concrete class" to be registered.
 */
static NNStreamer_custom_class {sname}_body = {{
  .initfunc = cg_init,
  .exitfunc = cg_exit,
  .getInputDim = cg_getInputDim,
  .getOutputDim = cg_getOutputDim,
  .setInputDim = cg_setInputDim,
  .invoke = cg_invoke,
  .allocate_invoke = cg_allocate_invoke,
  .destroy_notify = cg_destroy_notify,
}};

/**
 * @brief The dyn-loaded object.
 *
 * @todo @warning With #1182, this is to be updated.
 */
NNStreamer_custom_class *NNStreamer_custom = &{sname}_body;
"""

##
# @brief The meson build script for this custom filter
meson_script = """
project('{fname}', 'c',
  version: '1.0',
  license: ['LGPL'],
  meson_version: '>=0.40.0',
  default_options: [
    'warning_level=1',
  ]
)

cc = meson.get_compiler('c')

{fname}_prefix = get_option('prefix')
{fname}_libdir = join_paths({fname}_prefix, get_option('libdir'))
{fname}_bindir = join_paths({fname}_prefix, get_option('bindir'))
{fname}_includedir = join_paths({fname}_prefix, get_option('includedir'))

subplugin_install_prefix = join_paths({fname}_prefix, 'lib', 'nnstreamer')
customfilter_install_dir = join_paths(subplugin_install_prefix, 'customfilters')

# @todo Declare dependencies if you have libraries to use.
# example: glib_dep = dependency('glib-2.0')
# then, add it to "dependencies: ..." later.
glib_dep = dependency('glib-2.0')
gst_dep = dependency('gstreamer-1.0')
nnstreamer_dep = dependency('nnstreamer')

{fname}_srcfiles = [
  '{fname}.c'
]

{fname}_srcfiles_fullpath = []
foreach s : {fname}_srcfiles
  {fname}_srcfiles_fullpath += join_paths(meson.current_source_dir(), s)
endforeach

shared_library('{fname}',
  {fname}_srcfiles_fullpath,
  dependencies: [glib_dep, gst_dep, nnstreamer_dep],
  install: true,
  install_dir: customfilter_install_dir
)

# @warning NYI. Static library mode of custom filter is not supported yet.
# This will be supported after fixing #1182.
# static_library('{fname}',
#   {fname}_srcfiles_fullpath,
#   dependencies: [glib_dep, gst_dep, nnstreamer_dep],
#   install: true,
#   install_dir: {fname}_libdir,
# )
"""


## This is for debugging. To be removed.
today = date.today()

## 1. Ask for name.
name = getinput('Please enter the name of the nnstreamer custom filter: ')
sname = ''.join(re.findall(r"([a-zA-Z0-9_]+)", name))
def_fname = ''.join(re.findall(r"([a-zA-Z0-9_]+)", name))
## @todo @warning We may require prefix for all custom filter in later versions.
## 2. Ask/Check for fname (file & official custom filter name)
print('Please enter the custom filter name registered to tensor_filter.')
fname = getinput('Or press enter without name if ['+def_fname+'] is ok: ')
fname = ''.join(re.findall(r"([a-zA-Z0-9_]+)", fname))
if len(fname) < 1:
  fname = def_fname

result = common_head

## 3. Ask for options (dimension configuration modes)
while 1:
  option = getinput('Are dimensions of input/output tensors fixed? (yes/no):')
  option = option.lower()
  if option == 'y' or option == 'yes':
    result += dim_fixed
    break
  if option == 'n' or option == 'no':
    result += dim_variable
    break
  print("Please enter yes/y or no/n")

## 4. Ask for options (memory allocation modes)
while 1:
  option = getinput('Are you going to allocate output buffer in your code? (yes/no):')
  option = option.lower()
  if option == 'y' or option == 'yes':
    result += invoke_allocate
    break
  if option == 'n' or option == 'no':
    result += invoke_no_allocate
    break
  print("Please enter yes/y or no/n")

## 5. Generate .C file
result += common_tail
ccode = result.format(fname=fname, name=name, sname=sname, today=today)
cfile = open(fname+".c", "w")
cfile.write(ccode)
cfile.close()

## 6. Generate .meson file
mesoncode = meson_script.format(fname=fname, name=name, sname=sname, today=today)
mesonfile = open("meson.build", "w")
mesonfile.write(mesoncode)
mesonfile.close()
