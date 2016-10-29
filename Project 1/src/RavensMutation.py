from RavensHelpers import RavensHelpers


class RavensMutation:
    def __init__(self, source, target, dummy=False):
        self.helpers = RavensHelpers()
        self.referenced_properties = ['inside', 'above']
        self.refelection_axes = {
            'bottom-left': 'bottom'
        }
        self.isDummy = dummy
        self.source = source
        self.target = target
        self.mutations = []

        # Calculate mutation if its not a dummy mutation
        if not dummy:
            self.__addMutation(source, target)

    def __addMutation(self, object1, object2):
        if object2.name == 'DEL':
            self.mutations.append('DEL')
            return

        attribute_found = False
        for attribute_in_second in object2.attributes.items():
            for attribute_in_first in object1.attributes.items():
                if attribute_in_second == attribute_in_first:
                    attribute_found = True
                elif attribute_in_second[0] == attribute_in_first[0]:
                    # Skip referenced properties
                    if attribute_in_second[0] in self.referenced_properties:
                        attribute_found = True
                    elif attribute_in_first[0] == 'alignment':
                        attribute_found = True
                        axis = self.helpers.getAlignmentReflectionAxis(attribute_in_first[1], attribute_in_second[1])
                        if axis:
                            self.mutations.append(('reflect', axis))
                    elif attribute_in_first[0] == 'angle':
                        attribute_found = True
                        axis = self.helpers.getAngleRflectionAxis(attribute_in_first[1], attribute_in_second[1])
                        if axis:
                            self.mutations.append(('reflect', axis))
                    elif attribute_in_second[1] == attribute_in_first[1]:
                        attribute_found = True

            if not attribute_found:
                self.mutations.append(attribute_in_second)

            attribute_found = False
