#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;
modl_reg(){
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");

    fprintf(stderr," kv.mod");
    fprintf(stderr," na.mod");
    fprintf(stderr, "\n");
  }
  _kv_reg();
  _na_reg();
}
