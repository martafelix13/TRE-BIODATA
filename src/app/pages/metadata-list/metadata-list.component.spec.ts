import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MetadataListComponent } from './metadata-list.component';

describe('MetadataListComponent', () => {
  let component: MetadataListComponent;
  let fixture: ComponentFixture<MetadataListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MetadataListComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MetadataListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
