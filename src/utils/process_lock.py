import os
import fcntl
import atexit

class SingleInstanceLock:
    """Ensures only one instance of the bot is running."""
    
    def __init__(self, lockfile):
        self.lockfile = lockfile
        self.lockfd = None
        
    def acquire(self):
        """Try to acquire the lock."""
        try:
            self.lockfd = open(self.lockfile, 'w')
            fcntl.flock(self.lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.lockfd.write(str(os.getpid()))
            self.lockfd.flush()
            atexit.register(self.release)
            return True
        except (IOError, OSError):
            if self.lockfd:
                self.lockfd.close()
                self.lockfd = None
            return False
            
    def release(self):
        """Release the lock."""
        if self.lockfd:
            try:
                fcntl.flock(self.lockfd, fcntl.LOCK_UN)
                self.lockfd.close()
                os.unlink(self.lockfile)
            except (IOError, OSError):
                pass
            self.lockfd = None
