// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from custom_message:msg/MultiState.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGE__MSG__DETAIL__MULTI_STATE__STRUCT_H_
#define CUSTOM_MESSAGE__MSG__DETAIL__MULTI_STATE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'multiple_state'
#include "custom_message/msg/detail/state__struct.h"

/// Struct defined in msg/MultiState in the package custom_message.
typedef struct custom_message__msg__MultiState
{
  custom_message__msg__State__Sequence multiple_state;
} custom_message__msg__MultiState;

// Struct for a sequence of custom_message__msg__MultiState.
typedef struct custom_message__msg__MultiState__Sequence
{
  custom_message__msg__MultiState * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_message__msg__MultiState__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // CUSTOM_MESSAGE__MSG__DETAIL__MULTI_STATE__STRUCT_H_
