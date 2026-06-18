import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False

i = 0
while i < len(lines):
    line = lines[i]
    if "KATMAN 4: DERİN ANALİZ LABORATUVARI" in line:
        new_lines.append(line)
        new_lines.append("    st.markdown(\"<div class='streamlit-expanderHeader' style='margin-top: 10px;'>DERİN ANALİZ LABORATUVARI</div>\", unsafe_allow_html=True)\n")
        
        # skip the with st.expander line
        i += 1 
        
        # fix indentation for the inner block until we hit a blank line or KATMAN 5
        i += 1
        while i < len(lines) and not "KATMAN 5" in lines[i]:
            l = lines[i]
            if l.startswith("        "):
                new_lines.append(l[4:]) # remove 4 spaces
            elif l.strip() == "":
                new_lines.append(l)
            else:
                new_lines.append(l)
            i += 1
        continue
        
    elif "KATMAN 5: RİSK & STRATEJİ DOĞRULAMA" in line:
        new_lines.append(line)
        new_lines.append("    st.markdown(\"<div class='streamlit-expanderHeader' style='margin-top: 10px;'>RİSK & STRATEJİ DOĞRULAMA</div>\", unsafe_allow_html=True)\n")
        
        # skip the with st.expander line
        i += 1 
        
        # fix indentation for the inner block until we hit st.divider
        i += 1
        while i < len(lines) and not "st.divider()" in lines[i]:
            l = lines[i]
            if l.startswith("        "):
                new_lines.append(l[4:]) # remove 4 spaces
            elif l.strip() == "":
                new_lines.append(l)
            else:
                new_lines.append(l)
            i += 1
        continue

    new_lines.append(line)
    i += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("done")
