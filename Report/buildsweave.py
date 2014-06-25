''' Throwaway script to read in all pdf files in a directory; sort them, and
create a tex snippet for a composite report.  The .tex snippet is written to
./sweavesections/sweavetree.tex.  Some basic options and argparser are in place.

Most code here was written hastily and is unlikely to be useful.  Would not rec
as boilerplate.  Although it may work, stongly suggest not tampering with CONSTANTS.
In fact, names are hard-coded into the main tex report template, so not worth using.
'''

import os
import os.path as op
import argparse

import logging
logger = logging.getLogger(__name__)
from pyuvvis.logger import configure_logger

SECTIONREPORTSDIR = './sweavesections'
OUTNAME = 'sweavetree.tex'
TEMPFILES = ['.toc', '.log', '.aux', '.out', '.gz']


def ext(afile): 
    ''' return file extension, including "."  (eg  .txt)'''
    return op.splitext(afile)[1]


# Not robust: don't reuse 
def files_in_dir(directory):
    ''' Return abspath of files in directory; ignoring and warning if subdirectories.'''

    files = []    

    path = op.abspath(directory)
    for filename in os.listdir(directory):
        if op.isdir(filename):
            logger.warn('Subdirectory "%s" will be ignored!  Only files in "%s" ' 
                        'will be analyzed' % (filename, SECTIONREPORTSDIR) )
        else:
            files.append(op.join(op.abspath(directory) , filename))   

    return files

def parse():
    ''' Basic parser with three options: -c, -o, -r.  Returns ns.'''

    parser = argparse.ArgumentParser(prog='Sweave Template generator', 
                                     epilog='Parses .pdf files in "%s", and write covoluted pdfpages snippet to "%s".'
                                     % (SECTIONREPORTSDIR, OUTNAME), usage='python buildsweave.py --opts')

    parser.add_argument('-c', '--clean', action='store_true', 
                        help='Clean all files of type %s from  directory %s' % (TEMPFILES, SECTIONREPORTSDIR))

    parser.add_argument('-o', '--overwrite', action='store_true', 
                        help='If "%s" exists, overwrite it.' % op.join(SECTIONREPORTSDIR, OUTNAME))
    
    parser.add_argument('--pdf', action='store_true', 
                        help='Compiles any .tex files in the current working directory.  Shortcut to'
                        ' compiling the report after generating a new sweavefile')


    ### LEFT COMMENTED IN INCASE EVER COME TO FIX THIS FOR RSTUDIO
    #parser.add_argument('-r', '--runtexs', action='store_true', 
                        #help='Runs all .tex files that are encountered in "%s" directory (except %s). '
                        #'Basically, refreshes any pdfs that were not compiled fully.  Note, this runs '
                        #'pdflatex twice per file.'
                        #% (SECTIONREPORTSDIR, OUTNAME))

    return parser.parse_args()    

def main():

    ns = parse()

    configure_logger( screen_level='info', name=__name__ )
    logger.info( 'Logging initialized: set to info' )

    outfile = op.abspath( op.join(SECTIONREPORTSDIR, OUTNAME) )
    if op.exists(outfile) and not ns.overwrite:
        raise IOError( '%s ALREADY EXISTS.  Remove or rerun with -o flag.' % outfile )

    # Get all files; warn if directories found
    infiles = files_in_dir(SECTIONREPORTSDIR)

    ## Execute any outstanding tex files        
    #if ns.runtexs:    
        #texfiles = [f for f in infiles if ext(f) == '.tex']

        ## Don't run sweavetree.tex, only other tex files
        #if outfile in texfiles:
            #texfiles.remove( outfile )           

        ## pdflatex on all files
        #for tf in texfiles:
            #logger.info('Twice executing "pdflatex %s"' % tf)      
            ## Switch wd of auxilarry files will be written to .
            #wd = os.getcwd()
            #os.chdir(SECTIONREPORTSDIR)
            #os.system('pdflatex %s' % tf )
            #os.system('pdflatex %s' % tf )
            #os.chdir(wd)

        ## Regenerate files list as files have been udpated
        #infiles = files_in_dir(SECTIONREPORTSDIR)

    # Sort pdfs and make .tex snippet
    pdfs = [op.abspath(f) for f in infiles if ext(f) == '.pdf']
    if not pdfs:
        raise AttributeError( 'NO PDFS FOUND IN "%s"' % SECTIONREPORTSDIR )
    pdfs.sort()

    # Consider making different styles
    with open(outfile, 'w') as o:
        for idx, filename in enumerate(pdfs):

            # Take filename, replace '_' with '/' and remove .pdf to make section title
            # /foo/bar/f1_npsam.pdf ---> f1/npsam

            secname =  op.basename(filename).replace('_', '-').replace('.pdf', '')
            outfile = op.join(SECTIONREPORTSDIR, op.basename(filename))


            if idx == 0:
                sectionheading = '\section{Sectional Data Analysis}\subsection{%s}' % secname
            else:
                sectionheading = '\subsection{%s}' % secname                             

            o.write('\includepdf[pages=1, offset=25 0, pagecommand=%s]{%s}\n' % (sectionheading, outfile))
            o.write('\includepdf[pages=2-,pagecommand={}]{%s}\n' % outfile)    

    o.close()                
    logger.info('%s written.' % outfile)
    
    # Compile main report
    if ns.pdf:
        texfiles = [f for f in files_in_dir('.') if ext(f) == '.tex']
        if len(texfiles) > 1:
            logger.critical('There are more than one .tex files in this current'
                            ' directory.  Am not going to compile them...')
            
        elif len(texfiles) == 0:
            logger.warn('No tex files found in current directory: --pdf option ignored use')
            
        else:
            maintexfile = texfiles[0]
            os.system('pdflatex %s' % maintexfile )
            os.system('pdflatex %s' % maintexfile )

            
    # \includepdf[pages=1,pagecommand=\section{Sectional Data Analysis}
    # \subsection{Fiber1/NPSAM}]{foo.pdf}
    # \includepdf[pages=2,pagecommand={}]{foo.pdf}    

    # Clean up temporary tex files IN SWEAVESECTIONS       
    if ns.clean:
        logger.warn( "Removing all files of types %s in %s" % (TEMPFILES, SECTIONREPORTSDIR) )
        for filename in infiles:
            if ext(filename) in TEMPFILES:
                os.remove(filename)

        logger.warn( "Removing all files of types %s in CURRENT DIRECTORY" % TEMPFILES )
        for filename in files_in_dir('.'):
            if ext(filename) in TEMPFILES:
                os.remove(filename)

if __name__ == '__main__':
    main()