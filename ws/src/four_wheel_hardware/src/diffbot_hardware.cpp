#include "four_wheel_hardware/diffbot_hardware.hpp"
#include <cassert>
#include <chrono>
#include <hardware_interface/hardware_component_interface.hpp>
#include <hardware_interface/hardware_info.hpp>
#include <hardware_interface/lexical_casts.hpp>
#include <hardware_interface/system_interface.hpp>
#include <hardware_interface/types/hardware_interface_return_values.hpp>
#include <hardware_interface/types/hardware_interface_type_values.hpp>
#include <iomanip>
#include <rclcpp/logging.hpp>
#include <rclcpp/utilities.hpp>
#include <sstream>

// INFO: INIT
namespace four_wheel_hardware {
hardware_interface::CallbackReturn DiffBotSystemHardware::on_init(
    const hardware_interface::HardwareComponentInterfaceParams &params) {

  if (hardware_interface::SystemInterface::on_init(params) !=
      hardware_interface::CallbackReturn::SUCCESS) {
    return hardware_interface::CallbackReturn::ERROR;
  }

  this->hw_start_sec_ = hardware_interface::stod(
      info_.hardware_parameters["hw_start_duration_sec"]);

  this->hw_stop_sec_ = hardware_interface::stod(
      info_.hardware_parameters["hw_stop_duration_sec"]);
  // TODO:
  // add wheel specific code, like a struct or something
  //

  RCLCPP_INFO(get_logger(), "ON_INIT-------------------------------");

  for (const hardware_interface::ComponentInfo &joint : info_.joints) {
    if (joint.command_interfaces.size() != 1) {
      RCLCPP_FATAL(get_logger(),
                   "Joint '%s' has %zu command interfaces found. 1 expected.",
                   joint.name.c_str(), joint.command_interfaces.size());
      return hardware_interface::CallbackReturn::ERROR;
    }

    if (joint.command_interfaces[0].name !=
        hardware_interface::HW_IF_VELOCITY) {
      RCLCPP_FATAL(
          get_logger(),
          "Joint '%s' have %s command interfaces found. '%s' expected.",
          joint.name.c_str(), joint.command_interfaces[0].name.c_str(),
          hardware_interface::HW_IF_VELOCITY);
      return hardware_interface::CallbackReturn::ERROR;
    }

    // check number of state interfaces
    if (joint.state_interfaces.size() != 2) {
      RCLCPP_FATAL(get_logger(),
                   "Joint '%s' has %zu state interface. 2 expected.",
                   joint.name.c_str(), joint.state_interfaces.size());
      return hardware_interface::CallbackReturn::ERROR;
    }

    // check first is pos and secod is velocity
    if (joint.state_interfaces[0].name != hardware_interface::HW_IF_POSITION) {
      RCLCPP_FATAL(
          get_logger(),
          "Joint '%s' have '%s' as first state interface. '%s' expected.",
          joint.name.c_str(), joint.state_interfaces[0].name.c_str(),
          hardware_interface::HW_IF_POSITION);
      return hardware_interface::CallbackReturn::ERROR;
    }

    if (joint.state_interfaces[1].name != hardware_interface::HW_IF_VELOCITY) {
      RCLCPP_FATAL(
          get_logger(),
          "Joint '%s' have '%s' as second state interface. '%s' expected.",
          joint.name.c_str(), joint.state_interfaces[1].name.c_str(),
          hardware_interface::HW_IF_VELOCITY);
      return hardware_interface::CallbackReturn::ERROR;
    }
  }

  for (const hardware_interface::ComponentInfo &joint : info_.joints) {
    RCLCPP_INFO(get_logger(), "Joint name: %s", joint.name.c_str());

    RCLCPP_INFO(get_logger(), "Command interfaces:");
    for (const auto &cmd : joint.command_interfaces) {
      RCLCPP_INFO(get_logger(), "  - %s", cmd.name.c_str());
    }

    RCLCPP_INFO(get_logger(), "State interfaces:");
    for (const auto &state : joint.state_interfaces) {
      RCLCPP_INFO(get_logger(), "  - %s", state.name.c_str());
    }
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

// INFO: CONFIGURE
hardware_interface::CallbackReturn
DiffBotSystemHardware::on_configure(const rclcpp_lifecycle::State &) {

  RCLCPP_INFO(get_logger(), "ON "
                            "CONFIGURE-----------------------------------------"
                            "----------------------");

  for (const auto &[name, descr] : joint_state_interfaces_) {
    set_state(name, 0.0);
  }

  for (const auto &[name, descr] : joint_command_interfaces_) {
    set_command(name, 0.0);
  }
  RCLCPP_INFO(get_logger(), "Successfully configured!");
  return hardware_interface::CallbackReturn::SUCCESS;
}

// INFO: ACTIVATE
hardware_interface::CallbackReturn
DiffBotSystemHardware::on_activate(const rclcpp_lifecycle::State &) {
  RCLCPP_INFO(get_logger(),
              "ON_ACTIVATE--------------------------------------------------");

  for (int i = 0; i < this->hw_start_sec_; i++) {
    rclcpp::sleep_for(std::chrono::seconds(1));
    RCLCPP_INFO(get_logger(), "%.1f sec left..", hw_start_sec_ - i);
    // TODO:
    // add serial initialization to either /tty/ACM0 or /tty/USB0
  }

  for (const auto &[name, descr] : joint_state_interfaces_) {
    set_state(name, get_state(name));
    RCLCPP_INFO(get_logger(), "State Interface ---> %s", name.c_str());
  }

  for (const auto &[name, descr] : joint_command_interfaces_) {
    set_command(name, get_state(name));
    RCLCPP_INFO(get_logger(), "Command Interface ---> %s", name.c_str());
  }

  return hardware_interface::CallbackReturn::SUCCESS;
}

// INFO: DEACTIVATE
hardware_interface::CallbackReturn
DiffBotSystemHardware::on_deactivate(const rclcpp_lifecycle::State &) {

  RCLCPP_INFO(
      get_logger(),
      "ON_DEACTIVATE----------------------------------------------------");

  for (const auto &[name, descr] : joint_command_interfaces_) {
    set_command(name, 0.0);
  }

  for (auto i = 0; i < hw_stop_sec_; i++) {
    rclcpp::sleep_for(std::chrono::seconds(1));
    RCLCPP_INFO(get_logger(), "%.1f seconds left...", hw_stop_sec_ - i);
    // TODO:
    // add serial closing logic
  }
  return hardware_interface::CallbackReturn::SUCCESS;
}

// INFO: READ
hardware_interface::return_type
DiffBotSystemHardware::read(const rclcpp::Time &,
                            const rclcpp::Duration &period) {

  std::stringstream ss;
  ss << "READING STATUS";
  ss << std::fixed << std::setprecision(2);

  for (const auto &[name, descr] : joint_state_interfaces_) {
    if (descr.get_interface_name() == hardware_interface::HW_IF_POSITION) {

      auto velocity = get_command(descr.get_prefix_name() + "/" +
                                  hardware_interface::HW_IF_VELOCITY);

      set_state(name, get_state(name) + period.seconds() * velocity);
      // TODO:
      // read from serial motor data for the state interfaces

      ss << std::endl
         << "\t position " << get_state(name) << " and velocity " << velocity
         << " for '" << name << "'!";
    }
  }

  RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 500, "%s", ss.str().c_str());

  return hardware_interface::return_type::OK;
}

// INFO: WRITE
hardware_interface::return_type
DiffBotSystemHardware::write(const rclcpp::Time &, const rclcpp::Duration &) {

  std::stringstream ss;
  ss << "WRITING COMMANDS";
  for (const auto &[name, descr] : joint_command_interfaces_) {
    set_state(name, get_command(name));
    // TODO:
    // write from serial motor data for the command interfaces

    ss << std::fixed << std::setprecision(2) << std::endl
       << "\t" << "command " << get_command(name) << " for '" << name << "'!";
  }

  RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 500, "%s", ss.str().c_str());
  return hardware_interface::return_type::OK;
}

} // namespace four_wheel_hardware
  //
#include <pluginlib/class_list_macros.hpp>

PLUGINLIB_EXPORT_CLASS(four_wheel_hardware::DiffBotSystemHardware,
                       hardware_interface::SystemInterface)
