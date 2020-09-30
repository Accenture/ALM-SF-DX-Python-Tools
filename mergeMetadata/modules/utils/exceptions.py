class NotCreatedDescribeLog( Exception ):
	'''Exception launched when describe.log didn´t exist on the specific folder'''
	ERROR_CODE = 117

	def __init__( self, pathDescribe ):
		super().__init__( f'Describe log didnt exist, please place it on {pathDescribe}' )

class NoFullNameError( Exception ):

	def __init__( self, tagName ):
		super().__init__( f'No tag found for {tagName}' )