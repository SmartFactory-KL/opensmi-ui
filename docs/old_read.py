#     def read_model(self, machines: Mapping[str, RemoteMachine]):
#         for machine in machines.values():
#             components_to_process = deque[BaseRemoteComponent]([machine])
#
#             # TODO: Should really use the visitor pattern, as this chirade is also needed
#             # to get the signals
#             while components_to_process:
#                 next_component = components_to_process.popleft()
#
#                 # add component to cache
#                 self._component_cache.add(uuid.uuid4(), next_component)
#
#                 # add signals to message funnel
#                 next_component.status_changed.connect(
#                     callback=self.receiver.receive_component_state
#                 )
#
#                 next_component.notification_received.connect(
#                     callback=self.receiver.receive_component_notification
#                 )
#
#                 if (
#                     isinstance(next_component, RemoteMachine)
#                     and next_component.lock is not None
#                 ):
#                     next_component.lock.locked_changed.connect(
#                         callback=self.receiver.receive_lock_changed
#                     )
#                     next_component.lock.locking_user_changed.connect(
#                         callback=self.receiver.receive_lock_user_changed
#                     )
#
#                     for machine_user in next_component.users:
#                         machine_user.user_presence_changed.connect(
#                             callback=self.receiver.receive_user_presence_changed
#                         )
#
#                 # handle callables
#                 for skill_container in [
#                     next_component.skill_set,
#                     next_component.feasibility_check_set,
#                     next_component.precondition_check_set,
#                 ]:
#                     for skill in skill_container.values():
#                         self._callable_cache.add(uuid.uuid4(), skill)
#
#                         skill.state_changed.connect(
#                             callback=self.receiver.receive_skill_state
#                         )
#
#                         # handle skill variable trees
#                         for var_container in [
#                             skill.monitoring,
#                             skill.parameter_set,
#                             skill.final_result_data,
#                         ]:
#                             for variable in var_container:
#                                 self._add_var_container_references(variable)
#
#                 for method in next_component.method_set.values():
#                     self._callable_cache.add(uuid.uuid4(), method)
#                     # handle skill variable trees
#                     for var_container in [
#                         method.monitoring,
#                         method.parameter_set,
#                         method.final_result_data,
#                     ]:
#                         for variable in var_container:
#                             self._add_var_container_references(variable)
#
#                 # handle component variable trees
#                 for var_container in [
#                     next_component.monitoring,
#                     next_component.attributes,
#                     next_component.identification,
#                     next_component.parameter_set,
#                 ]:
#                     for variable in var_container:
#                         self._add_var_container_references(variable)
#
#                 for child in next_component.components.values():
#                     components_to_process.append(child)
