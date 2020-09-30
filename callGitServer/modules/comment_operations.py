''' Comment opterations Module '''
from modules.utils import MARKDOWN_BULLETS

def get_last_comment( workspace, buildId ):
    ''' Returns  '''
    with open( f'{workspace}/{buildId}-comment.txt', 'r+' ) as messageFile:
        comment     = messageFile.read().splitlines()
        commentId   = comment.pop( 0 ).strip()

    return commentId, comment

def append_new_comments( newComments, commentsHistory=[] ):
    ''' Returns the body of the comment after appending new messages '''
    for comment in newComments:
        if requires_blank_line( comment, commentsHistory ):
            commentsHistory.append( '' )

        commentsHistory.append( comment.rstrip() )
    return '\n'.join( commentsHistory )

def save_comment_to_file( comment, buildId, commentId, workspace, commentVersion=False ):
    ''' Saves message somewhere for future use '''
    with open( f'{workspace}/{buildId}-comment.txt', 'w' ) as commentFile:
        commentFile.write( f'{commentId}\n' )
        if commentVersion:
            commentFile.write( f'{commentVersion}\n' )
        commentFile.write( f'{comment}\n' )

def requires_blank_line( comment, commentsHistory ):
    ''' Returns, based on the previous commit, if it's necessary to write a
        new blank line in order to separate content due to MD formatting '''
    writeNewLine = True
    if not commentsHistory:
        writeNewLine = False
    elif ( comment.strip()[:2] in MARKDOWN_BULLETS and commentsHistory[-1].strip()[:2] in MARKDOWN_BULLETS ):
        # if new comment and last comment are bullets
        writeNewLine = False  
    return writeNewLine