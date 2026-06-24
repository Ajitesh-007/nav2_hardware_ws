#ifndef MY_ROBOT_HARDWARE__SERIAL_HARDWARE_INTERFACE_HPP_
#define MY_ROBOT_HARDWARE__SERIAL_HARDWARE_INTERFACE_HPP_

#include <string>
#include <vector>

#include "hardware_interface/system_interface.hpp"
#include "hardware_interface/handle.hpp"
#include "hardware_interface/hardware_info.hpp"
#include "hardware_interface/types/hardware_interface_return_values.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/state.hpp"

namespace my_robot_hardware
{

class SerialHardwareInterface : public hardware_interface::SystemInterface
{
public:
  RCLCPP_SHARED_PTR_DEFINITIONS(SerialHardwareInterface)

  hardware_interface::CallbackReturn on_init(
    const hardware_interface::HardwareInfo & info) override;

  hardware_interface::CallbackReturn on_configure(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_activate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_deactivate(
    const rclcpp_lifecycle::State & previous_state) override;

  hardware_interface::CallbackReturn on_cleanup(
    const rclcpp_lifecycle::State & previous_state) override;

  std::vector<hardware_interface::StateInterface> export_state_interfaces() override;
  std::vector<hardware_interface::CommandInterface> export_command_interfaces() override;

  hardware_interface::return_type read(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

  hardware_interface::return_type write(
    const rclcpp::Time & time, const rclcpp::Duration & period) override;

private:
  // Parameters from URDF
  std::string serial_port_;
  int baud_rate_;
  double wheel_radius_;
  double max_motor_speed_rad_s_;  // rad/s at PWM=255
  bool use_mock_hardware_ = false;  // skip serial port for bench testing

  // Serial file descriptor
  int serial_fd_ = -1;

  // ros2_control state & command storage
  // Index 0 = left_wheel_joint, Index 1 = right_wheel_joint
  std::vector<double> hw_positions_;
  std::vector<double> hw_velocities_;
  std::vector<double> hw_commands_;

  // Helper: open & configure serial port
  bool open_serial();
  void close_serial();
  bool send_command(int left_pwm, int right_pwm);
};

}  // namespace my_robot_hardware

#endif  // MY_ROBOT_HARDWARE__SERIAL_HARDWARE_INTERFACE_HPP_
