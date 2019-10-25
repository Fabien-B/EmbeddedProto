import io
import sys
import os
import jinja2

from google.protobuf.compiler import plugin_pb2 as plugin
from google.protobuf.descriptor_pb2 import DescriptorProto, FieldDescriptorProto, EnumDescriptorProto

# -----------------------------------------------------------------------------


class EnumTemplateParameters:
    def __init__(self, enum_proto):
        self.name = enum_proto.name
        self.enum_proto = enum_proto

    def values(self):
        for value in self.enum_proto.value:
            yield value


def generate_enums(enums):
    for enum in enums:
        yield EnumTemplateParameters(enum)

# -----------------------------------------------------------------------------


class FieldTemplateParameters:
    type_to_default_value = {FieldDescriptorProto.TYPE_DOUBLE:   "0.0",
                             FieldDescriptorProto.TYPE_FLOAT:    "0.0",
                             FieldDescriptorProto.TYPE_INT64:    "0",
                             FieldDescriptorProto.TYPE_UINT64:   "0U",
                             FieldDescriptorProto.TYPE_INT32:    "0",
                             FieldDescriptorProto.TYPE_FIXED64:  "0U",
                             FieldDescriptorProto.TYPE_FIXED32:  "0U",
                             FieldDescriptorProto.TYPE_BOOL:     "false",
                             FieldDescriptorProto.TYPE_STRING:   "TODO",    # TODO
                             FieldDescriptorProto.TYPE_MESSAGE:  "",
                             FieldDescriptorProto.TYPE_BYTES:    "TODO",    # TODO
                             FieldDescriptorProto.TYPE_UINT32:   "0U",
                             FieldDescriptorProto.TYPE_ENUM:     "0",
                             FieldDescriptorProto.TYPE_SFIXED32: "0",
                             FieldDescriptorProto.TYPE_SFIXED64: "0",
                             FieldDescriptorProto.TYPE_SINT32:   "0",
                             FieldDescriptorProto.TYPE_SINT64:   "0"}

    type_to_cpp_type = {FieldDescriptorProto.TYPE_DOUBLE:   "EmbeddedProto::doublefixed",
                        FieldDescriptorProto.TYPE_FLOAT:    "EmbeddedProto::floatfixed",
                        FieldDescriptorProto.TYPE_INT64:    "EmbeddedProto::int64",
                        FieldDescriptorProto.TYPE_UINT64:   "EmbeddedProto::uint64",
                        FieldDescriptorProto.TYPE_INT32:    "EmbeddedProto::int32",
                        FieldDescriptorProto.TYPE_FIXED64:  "EmbeddedProto::fixed64",
                        FieldDescriptorProto.TYPE_FIXED32:  "EmbeddedProto::fixed32",
                        FieldDescriptorProto.TYPE_BOOL:     "EmbeddedProto::boolean",
                        FieldDescriptorProto.TYPE_STRING:   "TODO",     # TODO
                        FieldDescriptorProto.TYPE_BYTES:    "TODO",     # TODO
                        FieldDescriptorProto.TYPE_UINT32:   "EmbeddedProto::uint32",
                        FieldDescriptorProto.TYPE_SFIXED32: "EmbeddedProto::sfixed32",
                        FieldDescriptorProto.TYPE_SFIXED64: "EmbeddedProto::sfixed64",
                        FieldDescriptorProto.TYPE_SINT32:   "EmbeddedProto::sint32",
                        FieldDescriptorProto.TYPE_SINT64:   "EmbeddedProto::sint64"}

    type_to_wire_type = {FieldDescriptorProto.TYPE_INT32:    "VARINT",
                         FieldDescriptorProto.TYPE_INT64:    "VARINT",
                         FieldDescriptorProto.TYPE_UINT32:   "VARINT",
                         FieldDescriptorProto.TYPE_UINT64:   "VARINT",
                         FieldDescriptorProto.TYPE_SINT32:   "VARINT",
                         FieldDescriptorProto.TYPE_SINT64:   "VARINT",
                         FieldDescriptorProto.TYPE_BOOL:     "VARINT",
                         FieldDescriptorProto.TYPE_ENUM:     "VARINT",
                         FieldDescriptorProto.TYPE_FIXED64:  "FIXED64",
                         FieldDescriptorProto.TYPE_SFIXED64: "FIXED64",
                         FieldDescriptorProto.TYPE_DOUBLE:   "FIXED64",
                         FieldDescriptorProto.TYPE_STRING:   "LENGTH_DELIMITED",
                         FieldDescriptorProto.TYPE_BYTES:    "LENGTH_DELIMITED",
                         FieldDescriptorProto.TYPE_MESSAGE:  "LENGTH_DELIMITED",
                         FieldDescriptorProto.TYPE_FIXED32:  "FIXED32",
                         FieldDescriptorProto.TYPE_FLOAT:    "FIXED32",
                         FieldDescriptorProto.TYPE_SFIXED32: "FIXED32"}

    type_to_ser_func = {FieldDescriptorProto.TYPE_DOUBLE:   "serialize",
                        FieldDescriptorProto.TYPE_FLOAT:    "serialize",
                        FieldDescriptorProto.TYPE_INT64:    "serialize",
                        FieldDescriptorProto.TYPE_UINT64:   "serialize",
                        FieldDescriptorProto.TYPE_INT32:    "serialize",
                        FieldDescriptorProto.TYPE_FIXED64:  "serialize",
                        FieldDescriptorProto.TYPE_FIXED32:  "serialize",
                        FieldDescriptorProto.TYPE_BOOL:     "serialize",
                        FieldDescriptorProto.TYPE_ENUM:     "serialize",
                        FieldDescriptorProto.TYPE_STRING:   "TODO",     # TODO
                        FieldDescriptorProto.TYPE_BYTES:    "TODO",     # TODO
                        FieldDescriptorProto.TYPE_UINT32:   "serialize",
                        FieldDescriptorProto.TYPE_SFIXED32: "serialize",
                        FieldDescriptorProto.TYPE_SFIXED64: "serialize",
                        FieldDescriptorProto.TYPE_SINT32:   "serialize",
                        FieldDescriptorProto.TYPE_SINT64:   "serialize"}

    type_to_deser_func = {FieldDescriptorProto.TYPE_DOUBLE:   "deserialize",
                          FieldDescriptorProto.TYPE_FLOAT:    "deserialize",
                          FieldDescriptorProto.TYPE_INT64:    "deserialize",
                          FieldDescriptorProto.TYPE_UINT64:   "deserialize",
                          FieldDescriptorProto.TYPE_INT32:    "deserialize",
                          FieldDescriptorProto.TYPE_FIXED64:  "deserialize",
                          FieldDescriptorProto.TYPE_FIXED32:  "deserialize",
                          FieldDescriptorProto.TYPE_BOOL:     "deserialize",
                          FieldDescriptorProto.TYPE_ENUM:     "deserialize",
                          FieldDescriptorProto.TYPE_STRING:   "TODO",     # TODO
                          FieldDescriptorProto.TYPE_BYTES:    "TODO",     # TODO
                          FieldDescriptorProto.TYPE_UINT32:   "deserialize",
                          FieldDescriptorProto.TYPE_SFIXED32: "deserialize",
                          FieldDescriptorProto.TYPE_SFIXED64: "deserialize",
                          FieldDescriptorProto.TYPE_SINT32:   "deserialize",
                          FieldDescriptorProto.TYPE_SINT64:   "deserialize"}

    def __init__(self, field_proto):
        self.name = field_proto.name
        self.variable_name = self.name + "_"
        self.variable_id_name = self.name + "_id"
        self.variable_id = field_proto.number

        self.of_type_message = FieldDescriptorProto.TYPE_MESSAGE == field_proto.type
        self.wire_type = self.type_to_wire_type[field_proto.type]
        if not self.of_type_message:
            self.serialization_func = self.type_to_ser_func[field_proto.type]
            self.deserialization_func = self.type_to_deser_func[field_proto.type]

        if FieldDescriptorProto.TYPE_MESSAGE == field_proto.type or FieldDescriptorProto.TYPE_ENUM == field_proto.type:
            self.type = field_proto.type_name if "." != field_proto.type_name[0] else field_proto.type_name[1:]
        else:
            self.type = self.type_to_cpp_type[field_proto.type]

        self.of_type_enum = FieldDescriptorProto.TYPE_ENUM == field_proto.type
        if self.of_type_enum:
            self.default_value = "static_cast<" + self.type + ">(0)"
        else:
            self.default_value = self.type_to_default_value[field_proto.type]

        self.is_repeated_field = field_proto.label == FieldDescriptorProto.LABEL_REPEATED
        if self.is_repeated_field:
            self.repeated_type = "::EmbeddedProto::RepeatedFieldSize<" + self.type + ", " + self.variable_name + "SIZE>"

        self.field_proto = field_proto

# -----------------------------------------------------------------------------


class MessageTemplateParameters:
    def __init__(self, msg_proto):
        self.name = msg_proto.name
        self.msg_proto = msg_proto
        self.templates = []
        for field in self.fields():
            if field.is_repeated_field:
                self.templates.append(field.variable_name)

    def fields(self):
        for f in self.msg_proto.field:
            yield FieldTemplateParameters(f)

    def nested_enums(self):
        for enum in self.msg_proto.enum_type:
            yield EnumTemplateParameters(enum)


def generate_messages(message_types):
    for msg in message_types:
        yield MessageTemplateParameters(msg)

# -----------------------------------------------------------------------------


def generate_code(request, respones):
    # Based upon the request from protoc generate

    template_loader = jinja2.FileSystemLoader(searchpath="./generator/")
    template_env = jinja2.Environment(loader=template_loader, trim_blocks=True, lstrip_blocks=True)
    template_file = "Header_Template.h"
    template = template_env.get_template(template_file)

    # Loop over all proto files in the request
    for proto_file in request.proto_file:

        if "proto2" == proto_file.syntax:
            raise Exception(proto_file.name + ": Sorry, proto2 is not supported, please use proto3.")

        messages_generator = generate_messages(proto_file.message_type)
        enums_generator = generate_enums(proto_file.enum_type)

        try:
            file_str = template.render(namespace=proto_file.package, messages=messages_generator, enums=enums_generator)
        except jinja2.TemplateError as e:
            print("TemplateError exception: " + str(e))
        except jinja2.UndefinedError as e:
            print("UndefinedError exception: " + str(e))
        except jinja2.TemplateSyntaxError as e:
            print("TemplateSyntaxError exception: " + str(e))
        except jinja2.TemplateRuntimeError as e:
            print("TemplateRuntimeError exception: " + str(e))
        except jinja2.TemplateAssertionError as e:
            print("TemplateAssertionError exception: " + str(e))
        except Exception as e:
            print("Template renderer exception: " + str(e))
        else:
            f = respones.file.add()
            f.name = os.path.splitext(proto_file.name)[0] + ".h"
            f.content = file_str


def main_plugin():
    # The main function when running the scrip as a protoc plugin. It will read in the protoc data from the stdin and
    # write back the output to stdout.

    # Read request message from stdin
    data = io.open(sys.stdin.fileno(), "rb").read()
    request = plugin.CodeGeneratorRequest.FromString(data)

    # Write the requests to a file for easy debugging.
    with open("./debug_request.bin", 'wb') as file:
        file.write(request.SerializeToString())

    # Create response
    response = plugin.CodeGeneratorResponse()

    # Generate code
    generate_code(request, response)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    io.open(sys.stdout.fileno(), "wb").write(output)


def main_cli():
    # The main function when running from the command line and debugging.  Instead of receiving data from protoc this
    # will read in a binary file stored the previous time main_plugin() is ran.

    with open("debug_request.bin", 'rb') as file:
        data = file.read()
        request = plugin.CodeGeneratorRequest.FromString(data)

        # Create response
        response = plugin.CodeGeneratorResponse()

        # Generate code
        generate_code(request, response)

        for response_file in response.file:
            print(response_file.name)
            print(response_file.content)

# -----------------------------------------------------------------------------


if __name__ == '__main__':
    # Check if we are running as a plugin under protoc
    if '--protoc-plugin' in sys.argv:
        main_plugin()
    else:
        main_cli()

# protoc --plugin=protoc-gen-eams=protoc-gen-eams --eams_out=./build ./test/proto/state.proto
