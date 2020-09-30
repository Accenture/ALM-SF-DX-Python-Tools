import os
import __main__

PWD					= os.path.dirname( os.path.realpath( __main__.__file__ ) )
REPORT_FILE			= 'pmd.log'
OUTPUT_FILE			= 'pmd.html'
SRC_PATH			= 'src\\'

KEY_LEVEL			= 'level'
KEY_SECTION			= 'section'
KEY_SUBSECTION		= 'subSection'
KEY_CLASSIFICATION	= 'classification'
DEFAUL_VALUE		= 'Not Classified'