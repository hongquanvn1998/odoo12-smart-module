# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import base_pb2 as base__pb2


class InstallAppStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.InstallApplication = channel.unary_unary(
                '/InstallApp/InstallApplication',
                request_serializer=base__pb2.AppRequest.SerializeToString,
                response_deserializer=base__pb2.AppResponse.FromString,
                )


class InstallAppServicer(object):
    """Missing associated documentation comment in .proto file."""

    def InstallApplication(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_InstallAppServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'InstallApplication': grpc.unary_unary_rpc_method_handler(
                    servicer.InstallApplication,
                    request_deserializer=base__pb2.AppRequest.FromString,
                    response_serializer=base__pb2.AppResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'InstallApp', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class InstallApp(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def InstallApplication(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/InstallApp/InstallApplication',
            base__pb2.AppRequest.SerializeToString,
            base__pb2.AppResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)