class RavensHelpers:
    def __init__(self):
        self.sizes = ['very small', 'small', 'medium', 'large', 'very large', 'huge']
        self.angle_reflections = {
            'x': [

            ],
            'y': [
                ['45', '135'],
                ['315', '225'],
                ['270', '0']
            ]
        }
        self.alignment_reflections = {
            'x': [
                ['top-left', 'top-right'],
                ['left', 'right'],
                ['bottom-left', 'bottom-right'],
            ],
            'y': [
                ['top-left', 'bottom-left'],
                ['top', 'bottom'],
                ['top-right', 'bottom-right']
            ]
        }

    def flipAlignment(self, axis, alignment):
        reflections = self.alignment_reflections[axis]
        for reflection in reflections:
            if reflection[0] == alignment:
                return reflection[1]
            elif reflection[1] == alignment:
                return reflection[0]

    def flipAngle(self, axis, angle):
        for axis in self.angle_reflections.items():
            for property in axis[1]:
                if property[0] == angle:
                    return property[1]
                elif property[1] == angle:
                    return property[0]

    def getAlignmentReflectionAxis(self, alignment1, alignment2):
        reflection_axis = False

        for axis in self.alignment_reflections.items():
            for property in axis[1]:
                if alignment1 == property[0] and alignment2 == property[1]:
                    reflection_axis = axis[0]
                elif alignment2 == property[0] and alignment1 == property[1]:
                    reflection_axis = axis[0]

        return reflection_axis

    def getAngleRflectionAxis(self, angle1, angle2):
        reflection_axis = False

        for axis in self.angle_reflections.items():
            for property in axis[1]:
                if angle1 == property[0] and angle2 == property[1]:
                    reflection_axis = axis[0]
                elif angle2 == property[0] and angle1 == property[1]:
                    reflection_axis = axis[0]

        return reflection_axis

    def getSizeOffset(self, size1, size2):
        test = self.sizes.index(size2) - self.sizes.index(size1)
        return self.sizes.index(size2) - self.sizes.index(size1)

    def getSizeAtOffset(self, current, offset):
        if not isinstance(offset, int):
            return current

        return self.sizes[self.sizes.index(current) + offset]

    def isSize(self, size):
        try:
            return self.sizes.index(size) >= 0
        except:
            return False
