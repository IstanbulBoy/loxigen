//:: # Copyright 2013, Big Switch Networks, Inc.
//:: #
//:: # LoxiGen is licensed under the Eclipse Public License, version 1.0 (EPL), with
//:: # the following special exception:
//:: #
//:: # LOXI Exception
//:: #
//:: # As a special exception to the terms of the EPL, you may distribute libraries
//:: # generated by LoxiGen (LoxiGen Libraries) under the terms of your choice, provided
//:: # that copyright and licensing notices generated by LoxiGen are not altered or removed
//:: # from the LoxiGen Libraries and the notice provided below is (i) included in
//:: # the LoxiGen Libraries, if distributed in source code form and (ii) included in any
//:: # documentation for the LoxiGen Libraries, if distributed in binary form.
//:: #
//:: # Notice: "Copyright 2013, Big Switch Networks, Inc. This library was generated by the LoxiGen Compiler."
//:: #
//:: # You may not use this file except in compliance with the EPL or LOXI Exception. You may obtain
//:: # a copy of the EPL at:
//:: #
//:: # http::: #www.eclipse.org/legal/epl-v10.html
//:: #
//:: # Unless required by applicable law or agreed to in writing, software
//:: # distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
//:: # WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
//:: # EPL for the specific language governing permissions and limitations
//:: # under the EPL.
//::
//:: from loxi_ir import *
//:: import itertools
//:: import of_g
//:: import java_gen.java_model as java_model
//:: include('_copyright.java')

//:: include('_autogen.java')

package ${test.package};

//:: include("_imports.java", msg=msg)
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

public class ${test.name} {
    //:: factory = java_model.model.factory_of(test.interface)
    //:: var_type = msg.interface.name
    //:: var_name = msg.interface.variable_name
    //:: builder_method = factory.method_name(msg.interface)
    //:: factory_impl = java_model.model.factory_of(test.interface).of_version(test.java_class.version).name
    ${factory.name if factory.name is not None else "OFFactory"} factory;

    final static byte[] ${msg.constant_name}_SERIALIZED =
        new byte[] { ${", ".join("%s0x%x" % (("" if ord(c)<128 else "(byte) "),  ord(c)) for c in test_data["binary"] ) } };

    @Before
    public void setup() {
        factory = ${factory_impl + ".INSTANCE" if factory_impl is not None else "OFFactories.getFactory(OFVersion." + version.constant_version + ")"};
    }

    //:: if "java" in test_data:
    @Test
    public void testWrite() {
        ${var_type}.Builder builder = factory.${builder_method}();
        ${test_data["java"]};
        ${var_type} ${var_name} = builder.build();
        ChannelBuffer bb = ChannelBuffers.dynamicBuffer();
        ${var_name}.writeTo(bb);
        byte[] written = new byte[bb.readableBytes()];
        bb.readBytes(written);

        assertArrayEquals(${msg.constant_name}_SERIALIZED, written);
    }

    @Test
    public void testRead() throws Exception {
        ${var_type}.Builder builder = factory.${builder_method}();
        ${test_data["java"]};
        ${var_type} ${var_name}Built = builder.build();

        ChannelBuffer input = ChannelBuffers.copiedBuffer(${msg.constant_name}_SERIALIZED);

        // FIXME should invoke the overall reader once implemented
        ${var_type} ${var_name}Read = ${msg.name}.READER.readFrom(input);
        assertEquals(${msg.constant_name}_SERIALIZED.length, input.readerIndex());

        assertEquals(${var_name}Built, ${var_name}Read);
   }
   //:: else:
   // FIXME: No java stanza in test_data for this class. Add for more comprehensive unit testing
   //:: #endif

   @Test
   public void testReadWrite() throws Exception {
       ChannelBuffer input = ChannelBuffers.copiedBuffer(${msg.constant_name}_SERIALIZED);

       // FIXME should invoke the overall reader once implemented
       ${var_type} ${var_name} = ${msg.name}.READER.readFrom(input);
       assertEquals(${msg.constant_name}_SERIALIZED.length, input.readerIndex());

       // write message again
       ChannelBuffer bb = ChannelBuffers.dynamicBuffer();
       ${var_name}.writeTo(bb);
       byte[] written = new byte[bb.readableBytes()];
       bb.readBytes(written);

       assertArrayEquals(${msg.constant_name}_SERIALIZED, written);
   }

}
