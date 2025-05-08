import { Injectable } from '@angular/core';
import { MatPaginatorIntl } from '@angular/material/paginator';
import { TranslateService } from '@ngx-translate/core';

@Injectable({ providedIn: 'root' })
export class CustomPaginatorIntl extends MatPaginatorIntl {
  constructor(private translate: TranslateService) {
    super();
    this.translateLabels();
    this.translate.onLangChange.subscribe(() => this.translateLabels());
  }

  translateLabels() {
    this.translate.get('paginator').subscribe((res: any) => {
      this.itemsPerPageLabel = res.itemsPerPageLabel;
      this.nextPageLabel = res.nextPageLabel;
      this.previousPageLabel = res.previousPageLabel;
      this.firstPageLabel = res.firstPageLabel;
      this.lastPageLabel = res.lastPageLabel;
      this.getRangeLabel = (page: number, pageSize: number, length: number) => {

        if (length === 0 || pageSize === 0) {
          return `0 di ${length}`;
        }
        const start = page * pageSize + 1;
        const end = Math.min((page + 1) * pageSize, length);
        if(res.rangeLabel.includes("di"))
          return `${start} - ${end} di ${length}`;
        else
          return `${start} - ${end} of ${length}`;
      };
      this.changes.next();
    });
  }
}
