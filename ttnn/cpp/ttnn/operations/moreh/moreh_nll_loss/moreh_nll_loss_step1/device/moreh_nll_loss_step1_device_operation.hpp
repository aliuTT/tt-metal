// SPDX-FileCopyrightText: © 2024 Tenstorrent Inc.
//
// SPDX-License-Identifier: Apache-2.0

#pragma once

#include "ttnn/decorators.hpp"
#include "ttnn/device_operation.hpp"
#include "ttnn/operations/core/compute_kernel/compute_kernel_config.hpp"
#include "ttnn/operations/moreh/moreh_nll_loss/moreh_nll_loss_helper.hpp"

namespace ttnn::operations::moreh::moreh_nll_loss_step1 {

struct MorehNllLossStep1DeviceOperation {
    struct operation_attributes_t {
        const std::string reduction = NONE;
        const uint32_t ignore_index = std::numeric_limits<uint32_t>::max();
        const DataType output_dtype;
        const uint32_t channel_size = 1;
        const MemoryConfig memory_config;
        const DeviceComputeKernelConfig compute_kernel_config;
    };

    struct tensor_args_t {
        const Tensor& target_tensor;
        const std::optional<Tensor>& weight_tensor;
    };

    using shape_return_value_t = Shape;

    using tensor_return_value_t = Tensor;

    struct Factory {
        struct shared_variables_t {
            KernelHandle unary_reader_kernel_id;
            KernelHandle unary_writer_kernel_id;
            std::size_t num_cores;
            std::size_t num_cores_y;
        };
        using cached_program_t = ttnn::device_operation::CachedProgram<shared_variables_t>;

        static cached_program_t create(
            const operation_attributes_t& operation_attributes,
            const tensor_args_t& tensor_args,
            tensor_return_value_t& tensor_return_value);

        static void override_runtime_arguments(
            cached_program_t& cached_program,
            const operation_attributes_t& operation_attributes,
            const tensor_args_t& tensor_args,
            tensor_return_value_t& tensor_return_value);
    };

    using program_factory_t = std::variant<Factory>;

    static program_factory_t select_program_factory(const operation_attributes_t&, const tensor_args_t&);

    static void validate_inputs(const operation_attributes_t& attributes, const tensor_args_t& tensor_args);

    static void validate_on_program_cache_miss(const operation_attributes_t&, const tensor_args_t&);

    static void validate_on_program_cache_hit(const operation_attributes_t&, const tensor_args_t&);

    static shape_return_value_t compute_output_shapes(const operation_attributes_t&, const tensor_args_t&);

    static tensor_return_value_t create_output_tensors(const operation_attributes_t&, const tensor_args_t&);

    static std::tuple<operation_attributes_t, tensor_args_t> invoke(
        const Tensor& target_tensor,
        const std::optional<Tensor>& weight_tensor,
        const int32_t ignore_index,
        const std::string reduction,
        const DataType output_dtype,
        const uint32_t channel_size,
        const std::optional<MemoryConfig>& memory_config,
        const DeviceComputeKernelConfig& compute_kernel_config);
};

}  // namespace ttnn::operations::moreh::moreh_nll_loss_step1

namespace ttnn::prim {
constexpr auto moreh_nll_loss_step1 = ttnn::register_operation<
    "ttnn::prim::moreh_nll_loss_step1",
    ttnn::operations::moreh::moreh_nll_loss_step1::MorehNllLossStep1DeviceOperation>();
}  // namespace ttnn::prim