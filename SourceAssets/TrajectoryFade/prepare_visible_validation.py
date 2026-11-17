from pathlib import Path
p=Path(__file__).parent
s=(p/'Validate.cs').read_text(encoding='utf-8-sig')
s=s.replace('validation.txt','validation_visible_contact.txt')
s=s.replace('name+".png"','"visible_"+name+".png"')
s=s.replace('zoom.SetZoomed(true);yield return new WaitForSeconds(.4f);Capture("b5_zoom");', '''Pitch(55);Aim();yield return new WaitForSeconds(.35f);Capture("b5_near_floor");
        Check("near B5 floor touched by guide shows circle",t.LandingMarkerVisible&&Length()<=2.501f);
        Pitch(0);Aim(true);yield return new WaitForSeconds(.3f);
        zoom.SetZoomed(true);yield return new WaitForSeconds(.4f);Capture("b5_zoom");''')
s=s.replace('Check("far collision retains a separate circle",t.PreviewHit&&t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,line.GetPosition(line.positionCount-1))>3f);', 'Check("far collision beyond guide hides circle",t.PreviewHit&&!t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,line.GetPosition(line.positionCount-1))>3f);')
s=s.replace('Check("zoom still stops before collision circle",t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,t.PreviewEnd)>2f);', 'Check("zoom still hides contact beyond guide",!t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,t.PreviewEnd)>2f);')
s=s.replace('Check("underhand far circle survives line cutoff",Mathf.Abs(Length()-2.5f)<.003f&&t.PreviewHit&&t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,t.PreviewEnd)>1f);', 'Check("underhand hides circle beyond cutoff",Mathf.Abs(Length()-2.5f)<.003f&&t.PreviewHit&&!t.LandingMarkerVisible&&Vector3.Distance(t.PreviewContact,t.PreviewEnd)>1f);')
s=s.replace('Check("wall circle follows hit normal",Mathf.Abs(t.PreviewNormal.z)>.95f);', '''Check("wall circle follows hit normal",Mathf.Abs(t.PreviewNormal.z)>.95f);
        Check("visible line meets circle on surface",Vector3.Distance(t.PreviewEnd,t.PreviewContact)<.012f);''')
s=s.replace('wall.SetActive(false);yield return new WaitForSeconds(.25f);', '''wall.transform.position=home+Vector3.forward*3.6f;Physics.SyncTransforms();yield return new WaitForSeconds(.25f);
        Check("normal guide does not reach middle wall",!t.LandingMarkerVisible);
        zoom.SetZoomed(true);yield return new WaitForSeconds(.4f);Capture("zoom_reaches_wall");
        Check("zoom guide reaching same wall shows circle",t.LandingMarkerVisible&&Length()<=4.001f&&Vector3.Distance(t.PreviewEnd,t.PreviewContact)<.012f);
        zoom.SetZoomed(false);yield return new WaitForSeconds(.4f);
        Check("zoom exit clears now unreachable circle",!t.LandingMarkerVisible);
        wall.SetActive(false);yield return new WaitForSeconds(.25f);''')
(p/'ValidateVisibleContact.cs').write_text(s,encoding='utf-8')
print('Prepared focused visible-contact checks.')
